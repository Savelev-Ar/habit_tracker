import json
from datetime import datetime, timedelta

import requests
from celery import shared_task
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from config.celery import app
from config.settings import BOT_TOKEN
from habit.models import Habit


@app.on_after_finalize.connect
def setup_periodic_tasks(**kwargs):
    set_tasks.delay()


@shared_task
def set_tasks():
    """
    Метод вызывается после старта сервера и инициализации проекта исполнителем (worker) django_celery_beat
    для получения из базы данных всех экземпляров привычек (Habit) и создания для каждого периодической задачи
    по уведомлению пользователя посредством бота Телеграм
    :return: None
    """
    habit_list = Habit.objects.exclude(is_pleasure=True)
    for habit in habit_list:
        habit_start_time = habit.start_time
        habit_start_date = habit.start_date
        current_date = timezone.localdate()
        current_time = timezone.localtime()
        # пропущено дней с даты первого выполнения действия
        lost_days = (current_date - habit_start_date).days
        # пропущено дней с последнего запланированного выполнения
        days_since_last = lost_days % habit.period
        # если действие запланировано на текущую дату определяем пропущено ли время выполнения или ещё не наступило
        if days_since_last == 0:
            start_time = datetime.combine(current_date, habit_start_time)
            if current_time.time() > habit_start_time:
                start_time = start_time + timedelta(days=habit.period)
        else:
            # дней до очередного запланированного выполнения
            days_to_action = habit.period - days_since_last
            start_time = datetime.combine(current_date, habit_start_time) + timedelta(
                days=days_to_action
            )
        # если пероидическая задача для данного действия не установлена, то устанавливаем
        if not PeriodicTask.objects.filter(
            name=f"Send notification: habit - {habit.pk}"
        ).exists():
            set_periodic_task(habit.pk, start_time)


@shared_task
def set_periodic_task(pk, time):
    """
    Метод создает в базе данных периодическую задачу, для последующего её исполнения
    исполнителем (worker) django_celery_beat.
    :param pk: id экземпляра привычки
    :param time: дата и время следующего старта периодической задачи
    :return: None
    """
    habit = Habit.objects.get(pk=pk)
    # Если задача для привычки уже существует, то при обновлении привычки (update) удаляем и создаем новую задачу
    if PeriodicTask.objects.filter(name=f'Send notification: habit - {habit.pk}').exists():
        PeriodicTask.objects.get(name=f'Send notification: habit - {habit.pk}').delete()
    if habit.owner.tele_id:
        # Если у пользователя заполнено поле id пользователя в Телеграм, то создаем задачу
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24 * habit.frequency,
            period=IntervalSchedule.HOURS,)
        PeriodicTask.objects.create(
            interval=schedule,
            name=f'Send notification: habit - {pk}',
            task='habit.tasks.send_notification',
            kwargs=json.dumps(
                {
                    "chat_id": habit.owner.tele_id,
                    "message": f"Уведомляем о наступлении времени выполнения полезной привычки: {habit}",
                }
            ),
            start_time=time,)


@shared_task
def send_notification(chat_id, message):
    """
    Метод вызывается в запланированное время исполнителем (worker) django_celery_beat.
    Отправляет через API Telegram пользователю уведомление о запланированном действии
    :param chat_id: id пользователя в системе Телеграм
    :param message: текст сообщения пользователю
    :return:
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        headers=headers,
        data=data,
    )
    if response.status_code == 200:
        return "ok"

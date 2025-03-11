from django.db import models

from user.models import User

NULLABLE = {'blank': True, 'null': True}


class Habit(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner_habit',
        verbose_name='Пользователь')

    location = models.CharField(
        max_length=100,
        verbose_name='Место',
        **NULLABLE)

    start_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата первого выполнения',
        help_text='Укажите дату первого выполнения привычки',
        **NULLABLE,
    )
    start_time = models.TimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Время выполнения привычки',
        help_text='Время выполнения привычки в секундах',
        **NULLABLE)
    action = models.CharField(
        max_length=200,
        verbose_name='Действие')
    is_pleasure = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки')
    linked_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        verbose_name='Связанная привычка',
        help_text='Укажите приятную привычку',
        **NULLABLE)
    period = models.SmallIntegerField(
        default=1,
        verbose_name='Периодичность',
        help_text='Укажите периодичность выполнения привычки в днях',
    )
    prize = models.CharField(
        max_length=200,
        verbose_name='Вознаграждение',
        **NULLABLE)
    action_time = models.SmallIntegerField(
        default=120,
        verbose_name='Время на выполнение',
        help_text='Укажите время на выполнение в секундах')
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности')


    def __str__(self):
        return f'Я буду: {self.action} в {self.start_time} в {self.location}'

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['owner']

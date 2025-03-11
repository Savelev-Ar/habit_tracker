from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from habit.models import Habit
from habit.serializers import HabitSerializer
from habit.tasks import set_periodic_task
from user.permissions import IsOwner


class HabitListView(generics.ListAPIView):
    """
    Контроллер отвечает за отображение списка публичных привычек (is_public=True),
    доступных всем авторизованным пользователям
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.all().filter(is_public=True)


class HabitCreateView(generics.CreateAPIView):
    """
    Контроллер отвечает за создание экземпляра привычки (model Habit)
    текущим авторизованным пользователем
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Метод выполняет действия при создании экземпляра привычки (model Habit)
        текущим авторизованным пользователем
        :param serializer:
        :return:
        """
        habit = serializer.save()
        habit.owner = self.request.user
        habit.save()
        start_time = datetime.combine(habit.start_date, habit.start_time)
        set_periodic_task.delay(habit.pk, start_time)


class HabitUpdateView(generics.UpdateAPIView):
    """
    Контроллер отвечает за обновление экземпляра привычки (model Habit)
    текущим авторизованным пользователем
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsOwner]

    def perform_update(self, serializer):
        """
        Метод реализует действия при обновлении существующего экземпляра
        привычки (Habit)
        :param serializer:
        :return: None
        """
        habit = serializer.save()
        current_date = timezone.localdate()
        current_time = timezone.localtime()
        # если текущая дата больше даты первого запланированного выполнения действия
        if current_date > habit.start_date:
            # пропущено дней с даты первого выполнения действия
            lost_days = (current_date - habit.start_date).days
            # пропущено дней с последнего запланированного выполнения
            days_since_last = lost_days % habit.period
            if days_since_last == 0:
                habit_start_time = datetime.combine(current_date, habit.start_time)
                if current_time.time() > habit.start_time:
                    habit_start_time = habit_start_time + timedelta(days=habit.period)
            else:
                # дней до очередного запланированного выполнения
                days_to_action = habit.period - days_since_last
                habit_start_time = datetime.combine(
                    current_date, habit.start_time
                ) + timedelta(days=days_to_action)
        else:
            habit_start_time = datetime.combine(habit.start_date, habit.start_time)
        set_periodic_task.delay(habit.pk, habit_start_time)


class HabitDestroyView(generics.DestroyAPIView):
    """
    Контроллер отвечает за удаление привычки пользователем
    """

    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsOwner]

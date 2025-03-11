from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from habit.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Класс сериализатора для работы с данными модели Habit
    """

    def validate(self, attrs):
        """
        Метод проверяет поля экземпляра habit при его создании или обновлении
        на соответствие требованиям
        :param attrs: словарь значений полей
        :return attrs: словарь проверенных значений
        """

        linked_habit = None
        prize = None
        action_time = None
        is_pleasure = None
        period = None
        """Если происходит обновление данных экземпляра (методы 'PUT', 'PATCH')
        отсутствующие значения полей получаем из объекта в базе данных"""
        if self.instance:
            linked_habit = getattr(self.instance, "linked_habit")
            prize = getattr(self.instance, "prize")
            action_time = getattr(self.instance, "action_time")
            is_pleasure = getattr(self.instance, "is_pleasure")
            period = getattr(self.instance, "period")
        """Если в контроллер передаются указанные свойства
        перезаписываем переменные их значениями"""
        if attrs.get("bound_habit"):
            linked_habit = attrs.get("linked_habit")
        if attrs.get("prize"):
            prize = attrs.get("prize")
        if attrs.get("action_time"):
            action_time = attrs.get("action_time")
        if attrs.get("is_pleasure"):
            is_pleasure = attrs.get("is_pleasure")
        if attrs.get("period"):
            period = attrs.get("period")
        # Производим валидацию переданных данных
        if linked_habit and prize:
            raise ValidationError(
                "You cannot set field <linked_habit> and <prize> concurrently"
            )
        if linked_habit:
            if not linked_habit.is_pleasure:
                raise ValidationError(
                    "linked habit must be with set attribute <is_pleasure"
                )
        if is_pleasure:
            if linked_habit or prize:
                raise ValidationError(
                    "Pleasure habit must not have linked habit or prize"
                )
        if action_time > 120:
            raise ValidationError("action_time must be up to 120 seconds")
        if period > 7:
            raise ValidationError(
                "You cannot period action less often then one time at 7 days"
            )
        return attrs

    class Meta:
        model = Habit
        fields = "__all__"

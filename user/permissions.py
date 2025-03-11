from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Класс определяет доступ к экземпляру привычки (model Habit)
    Если создателем привычки является текущий пользователь, то он имеет доступ к просмотру и редактированию
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

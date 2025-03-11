from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from habit.models import Habit
from habit.paginators import HabitPaginator
from habit.serializers import HabitSerializer
from user.models import User
from user.permissions import IsOwner
from user.serializers import UserSerializer, UserTokenObtainPairSerializer


class UserCreateView(generics.CreateAPIView):
    """
    Контроллер отвечает за создание в базе данных нового пользователя (model User)
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        if user.tele_user.startswith("@"):
            user.tele_user = user.tele_user.lstrip("@")
        user.save()


class UserHabitListView(generics.ListAPIView):
    """
    Контроллер отвечает за отображение списка привычек, созданных
    текущим авторизованным пользователем
    """

    serializer_class = HabitSerializer
    permission_classes = [IsOwner]
    pagination_class = HabitPaginator

    def get_queryset(self):
        user = self.request.user
        return Habit.objects.all().filter(owner=user)


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer
    permission_classes = [AllowAny]

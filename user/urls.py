from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from user.apps import UserConfig
from user.views import UserCreateView, UserHabitListView, UserTokenObtainPairView

app_name = UserConfig.name

urlpatterns = [
    path('create/', UserCreateView.as_view(permission_classes=[AllowAny]), name='user_create'),
    path('login/', UserTokenObtainPairView.as_view(permission_classes=[AllowAny]), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=[AllowAny]), name='token_refresh'),
    path('user/habits/', UserHabitListView.as_view(), name='user_habits'),
]

from django.urls import path

from habit.apps import HabitConfig
from habit.views import (HabitCreateView,
                         HabitDestroyView,
                         HabitListView,
                         HabitUpdateView)

app_name = HabitConfig.name

urlpatterns = [
    path("habits/list/", HabitListView.as_view(), name="public_habits"),
    path("habits/create/", HabitCreateView.as_view(), name="habit_create"),
    path("habits/update/<int:pk>/", HabitUpdateView.as_view(), name="habit_update"),
    path("habits/delete/<int:pk>/", HabitDestroyView.as_view(), name="habit_delete"),
]

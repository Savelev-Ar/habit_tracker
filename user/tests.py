from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from habit.models import Habit
from user.models import User


class HabitTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email='test@test.ru', tele_user='@saver_s')
        self.habit = Habit.objects.create(
            action='Выпить стакан воды',
            start_date=timezone.now().date(),
            start_time=timezone.now().time(),
            action_time=120,
            period=1,
            owner=self.user,
        )
        self.client.force_authenticate(user=self.user)

    def test_get_user_list(self):
        url = reverse('user:user_habits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_user(self):
        url = reverse('user:user_create')
        self.data = {
            "email": "test@test.com",
            "password": "test",
            "tele_user": "test",
        }
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

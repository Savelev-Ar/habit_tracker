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

    def test_get_list(self):
        url = reverse('habit:public_habits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_habit(self):
        self.data = {
            "action": "Отжаться от пола",
            "start_date": timezone.now().date(),
            "start_time": timezone.now().time(),
            "action_time": 100,
            "period": 1,
            "owner": self.user.pk,
        }
        url = reverse('habit:habit_create')
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_habit(self):
        url = reverse('habit:habit_update', kwargs={"pk": self.habit.pk})
        self.data = {"action": "Съесть банан"}
        response = self.client.patch(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_habit(self):
        """
        Тестовый случай для проверки метода validate сериализатора
        """
        url = reverse('habit:habit_update', kwargs={"pk": self.habit.pk})
        self.data = {"action_time": 200}
        response = self.client.patch(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_habit(self):
        url = reverse('habit:habit_delete', kwargs={"pk": self.habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Exception):
            Habit.objects.get(pk=self.habit.pk)

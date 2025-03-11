from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='Электропочта')

    tele_id = models.CharField(
        max_length=12,
        unique=True,
        verbose_name='ID в телеграмм',
        **NULLABLE)

    tele_user = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='username пользователя в телеграм',
        help_text='Укажите свой @username в Telegram')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['tele_user']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']

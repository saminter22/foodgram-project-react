from django.contrib.auth import get_user_model

from django.urls import reverse
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class User(AbstractUser):
    """Кастомная модель пользователя"""
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
        null=False,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # objects = UserManager()

    class Meta:
            ordering = ('username', )
            verbose_name = 'Пользователь'
            verbose_name_plural = 'Пользователи'

    def __str__(self):
        # return f'{self.username} - {self.email}'
        return self.username

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'user': self.username})

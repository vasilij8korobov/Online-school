from django.contrib.auth.models import AbstractUser
from django.db import models

from DRY import NULLABLE


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    phone = models.CharField(
        max_length=15,
        **NULLABLE,
        verbose_name='Телефон'
    )
    city = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name='Город'
    )
    avatar = models.ImageField(
        upload_to='images/avatars/',
        **NULLABLE,
        verbose_name='Аватарка'
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='Группы, к которым принадлежит пользователь. Пользователь получит все разрешения, предоставленные каждой из его групп.',
        verbose_name='Группы'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Конкретные разрешения для этого пользователя.',
        verbose_name='Разрешения пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

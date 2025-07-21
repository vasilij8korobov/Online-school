from datetime import timedelta

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone


@shared_task
def deactivate_inactive_users():
    # Вычисляем дату, которая была месяц назад
    one_month_ago = timezone.now() - timedelta(days=30)

    # Находим пользователей, которые не заходили более месяца
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    # Блокируем найденных пользователей
    inactive_users.update(is_active=False)

import logging

from django.conf import settings
from django.core.mail import send_mail

from config.celery import app
from celery import shared_task

from materials.models import Course, Subscription

logger = logging.getLogger(__name__)


@shared_task
def send_update_notification(course_id):
    course = Course.objects.get(id=course_id)
    subscribers = Subscription.objects.filter(course=course)
    for subscriber in subscribers:
        send_mail(
            'Обновление курса',
            f'Курс {course.name} был обновлен.',
            settings.DEFAULT_FROM_EMAIL,
            [subscriber.user.email],
            fail_silently=False,
        )


# @shared_task
# def example_task():
#     logger.info("Пример периодической задачи выполнен")
#     return "Задача выполнена успешно"
#
#
# @app.task
# def my_periodic_task():
#     return print("Выполнение периодической задачи")

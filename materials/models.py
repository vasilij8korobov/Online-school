from django.db import models

from DRY import NULLABLE
from django.conf import settings


class Course(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    preview = models.ImageField(
        upload_to='images/course_previews/',
        **NULLABLE,
        verbose_name='Превью'
    )
    description = models.TextField(
        verbose_name='Описание',
        **NULLABLE
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        **NULLABLE,
        on_delete=models.CASCADE,
        related_name='courses'
    )

    materials_link = models.URLField(
        **NULLABLE,
        verbose_name="Ссылка на материалы курса"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Lesson(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание',
        **NULLABLE
    )
    preview = models.ImageField(
        upload_to='images/lesson_previews/',
        **NULLABLE,
        verbose_name='Превью'
    )
    video_link = models.URLField(
        verbose_name='Ссылка на видео',
        **NULLABLE
    )
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        **NULLABLE,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    materials_link = models.URLField(
        **NULLABLE,
        verbose_name="Ссылка на материалы урока"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_subscriptions',
        verbose_name='Пользователь')
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='user_subscriptions',
        verbose_name='Курс')
    subscribed_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата подписки')

    class Meta:
        unique_together = ('user', 'course')  # Одна подписка на пользователя и курс
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-subscribed_at']

    def __str__(self):
        return f'{self.user.email} подписан на {self.course}'  # type: ignore

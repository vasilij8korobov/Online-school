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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

# Generated by Django 5.2 on 2025-05-04 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0002_alter_course_options_alter_lesson_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='course',
            name='preview',
            field=models.ImageField(blank=True, null=True, upload_to='images/course_previews/', verbose_name='Превью'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='preview',
            field=models.ImageField(blank=True, null=True, upload_to='images/lesson_previews/', verbose_name='Превью'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video_link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на видео'),
        ),
    ]

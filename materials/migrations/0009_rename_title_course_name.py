# Generated by Django 5.2 on 2025-05-14 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0008_rename_name_course_title_rename_name_lesson_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='title',
            new_name='name',
        ),
    ]

# Generated by Django 5.2 on 2025-05-04 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_customuser_options_alter_customuser_avatar_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='images/avatars/', verbose_name='Аватарка'),
        ),
    ]

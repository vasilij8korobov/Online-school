from django.contrib.auth.models import AbstractUser
from django.db import models

from DRY import NULLABLE
from materials.models import Course, Lesson


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


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счёт'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        **NULLABLE,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        **NULLABLE,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )

    # Новые поля для Stripe
    stripe_product_id = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name='ID продукта в Stripe'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name='ID цены в Stripe'
    )
    stripe_session_id = models.CharField(
        max_length=100,
        **NULLABLE,
        verbose_name='ID сессии в Stripe'
    )
    stripe_payment_link = models.URLField(
        max_length=512,
        **NULLABLE,
        verbose_name='Ссылка на оплату Stripe'
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Оплачено'
    )
    stripe_payment_status = models.CharField(
        max_length=20,
        **NULLABLE,
        verbose_name='Статус платежа в Stripe'
    )

    def __str__(self):
        return f"{self.user.email} - {self.amount} руб. ({self.payment_date})"

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Payment, CustomUser


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        extra_kwargs = {
            'user': {
                'help_text': 'Пользователь, совершивший платеж'
            },
            'payment_date': {
                'help_text': 'Дата и время совершения платежа',
                'format': '%Y-%m-%d %H:%M:%S'
            },
            'paid_course': {
                'help_text': 'Оплаченный курс (может быть пустым если оплачен урок)'
            },
            'paid_lesson': {
                'help_text': 'Оплаченный урок (может быть пустым если оплачен курс)'
            },
            'amount': {
                'help_text': 'Сумма оплаты в рублях'
            },
            'payment_method': {
                'help_text': 'Способ оплаты: cash - наличные, transfer - перевод, stripe - оплата картой'
            },
            'stripe_id': {
                'help_text': 'Идентификатор платежа в Stripe (только для Stripe-платежей)',
                'required': False
            },
            'stripe_status': {
                'help_text': 'Статус платежа в Stripe: pending, paid, failed',
                'required': False
            },
            'stripe_url': {
                'help_text': 'Ссылка на страницу оплаты Stripe',
                'required': False
            }
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'phone', 'city', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )
        return user


class StripePaymentResponseSerializer(serializers.Serializer):
    payment_url = serializers.URLField()
    payment_id = serializers.IntegerField(required=False)

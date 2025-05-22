from datetime import date

from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from config.services.stripe_service import create_stripe_product, create_stripe_price, create_stripe_checkout_session
from materials.models import Course
from users.filters import PaymentFilter
from users.models import Payment, CustomUser
from users.permissions import IsAdminOrOwner
from users.serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer, StripePaymentResponseSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


@extend_schema(
    tags=['Платежи'],
    description='Управление платежами пользователей'
)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter

    @extend_schema(
        summary='Список платежей',
        description='Возвращает отфильтрованный список платежей с возможностью пагинации',
        parameters=[
            OpenApiParameter(
                name='course',
                type=int,
                description='Фильтр по ID курса',
                required=False
            ),
            OpenApiParameter(
                name='payment_method',
                type=str,
                description='Фильтр по способу оплаты (cash/transfer)',
                required=False
            ),
            OpenApiParameter(
                name='date_after',
                type=date,
                description='Фильтр по дате (платежи после указанной даты)',
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Пример ответа',
                value=[
                    {
                        "id": 1,
                        "user": 1,
                        "payment_date": "2023-10-15T12:00:00Z",
                        "course": 5,
                        "amount": 10000,
                        "payment_method": "transfer"
                    }
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(
    tags=['Пользователи'],
    description='Управление пользователями (только для администраторов)'
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    @extend_schema(
        summary='Получение профиля пользователя',
        description='Возвращает полную информацию о пользователе',
        responses={
            200: UserSerializer,
            403: {'description': 'У вас нет прав доступа к этому профилю'}
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        exclude=True
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(
    tags=['Аутентификация'],
    summary='Регистрация нового пользователя',
    description='Создает нового пользователя в системе',
    request=UserRegisterSerializer,
    responses={
        201: UserRegisterSerializer,
        400: {
            'description': 'Невалидные данные',
            'examples': {
                'application/json': {
                    'username': ['Это поле обязательно.'],
                    'password': ['Пароль слишком простой.']
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "email": "user@example.com",
                "password": "securepassword123",
                "password2": "securepassword123"
            },
            request_only=True
        )
    ]
)
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=['Аутентификация'],
    summary='Получение JWT токена',
    description='Возвращает access и refresh токены для аутентификации',
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    },
    responses={
        200: {
            'description': 'Успешная аутентификация',
            'content': {
                'application/json': {
                    'example': {
                        'access': 'eyJhbGciOi...',
                        'refresh': 'eyJhbGciOi...'
                    }
                }
            }
        },
        401: {
            'description': 'Неверные учетные данные',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'No active account found with the given credentials'
                    }
                }
            }
        }
    },
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "email": "user@example.com",
                "password": "securepassword123"
            },
            request_only=True
        )
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=['Платежи'],
    description='Создание платежа через Stripe'
)
class StripePaymentCreateAPIView(APIView):
    """Создание платежной сессии Stripe для курса"""
    permission_classes = [IsAuthenticated]
    serializer_class = StripePaymentResponseSerializer

    @extend_schema(
        summary='Создать платеж Stripe',
        responses={
            201: {
                'description': 'Ссылка для оплаты',
                'content': {
                    'application/json': {
                        'example': {
                            'payment_id': 1,
                            'payment_link': 'https://checkout.stripe.com/pay/...'
                        }
                    }
                }
            },
            404: {'description': 'Курс не найден'},
            400: {'description': 'Ошибка создания платежа'}
        }
    )
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)

            # Создаем продукт в Stripe
            product = create_stripe_product(
                name=f'Курс: {course.name}',
                description=course.description[:500]
            )

            # Создаем цену в Stripe (умножаем на 100 для перевода в копейки)
            price = create_stripe_price(
                product_id=product.id,
                amount=course.price * 100 if course.price else 0
            )

            # URL для редиректа после оплаты
            success_url = request.build_absolute_uri(
                reverse('payment-success') + f'?session_id={{CHECKOUT_SESSION_ID}}'
            )
            cancel_url = request.build_absolute_uri(
                reverse('payment-cancel')
            )

            # Создаем сессию оплаты в Stripe
            session = create_stripe_checkout_session(
                price_id=price.id,
                success_url=success_url,
                cancel_url=cancel_url
            )

            # Сохраняем платеж в БД
            payment = Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount=course.price,
                payment_method='stripe',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                stripe_payment_link=session.url
            )

            return Response({
                'payment_id': payment.id,
                'payment_link': session.url
            }, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Курс не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentSuccessAPIView(APIView):
    """Обработка успешной оплаты"""

    def get(self, request):
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                payment = Payment.objects.get(stripe_session_id=session_id)
                payment.is_paid = True
                payment.stripe_payment_status = 'paid'
                payment.save()
                return Response({'status': 'Payment successful'})
            except Payment.DoesNotExist:
                pass
        return Response({'status': 'Payment processed'})


class PaymentCancelAPIView(APIView):
    """Обработка отмены оплаты"""

    def get(self, request):
        return Response(
            {'status': 'Payment can be paid later'},
            status=status.HTTP_200_OK
        )

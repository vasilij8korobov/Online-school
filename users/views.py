from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from users.filters import PaymentFilter
from users.models import Payment, CustomUser
from users.permissions import IsAdminOrOwner
from users.serializers import PaymentSerializer, UserSerializer, UserRegisterSerializer

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
        exclude=True  # Скрываем стандартные методы, если не хотим их документировать
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

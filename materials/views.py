from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from .paginators import CoursePagination, LessonPagination  # Импортируем классы пагинации
from users.permissions import IsModerator, IsOwner

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.annotate(
        lessons_count=models.Count('lessons')).prefetch_related('lessons')
    serializer_class = CourseSerializer
    pagination_class = CoursePagination  # Добавляем пагинацию для курсов

    def get_permissions(self):
        """Динамическое определение прав доступа в зависимости от действия"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматическое назначение владельца при создании курса"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация queryset в зависимости от роли пользователя"""
        if self.request.user.is_staff or self.request.user.groups.filter(name='moderators').exists():
            return super().get_queryset()
        return Course.objects.filter(owner=self.request.user)

    @extend_schema(
        summary='Список курсов',
        description='Возвращает список всех курсов с пагинацией. '
                    'Обычные пользователи видят только свои курсы, '
                    'модераторы и администраторы - все.',
        parameters=[
            OpenApiParameter(
                name='page',
                type=int,
                description='Номер страницы для пагинации',
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Пример ответа',
                value={
                    "count": 10,
                    "next": "http://api.example.com/courses/?page=2",
                    "previous": None,
                    "results": [
                        {"id": 1, "title": "Курс 1", "lessons_count": 5},
                    ]
                }
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Создание курса',
        description='Создает новый курс. Владелец назначается автоматически.',
        request=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPagination  # Добавляем пагинацию для уроков

    def get_permissions(self):
        """Динамическое определение прав доступа в зависимости от действия"""
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматическое назначение владельца при создании урока"""
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """Фильтрация queryset в зависимости от роли пользователя"""
        if self.request.user.is_staff or self.request.user.groups.filter(name='moderators').exists():
            return super().get_queryset()
        return Lesson.objects.filter(owner=self.request.user)

    @extend_schema(
        summary='Создание урока',
        description='Создает новый урок в курсе. Требуются права владельца курса.',
        request=LessonSerializer,
        responses={
            201: LessonSerializer,
            403: {"description": "У вас нет прав на создание урока в этом курсе"}
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


@extend_schema(
    tags=['Подписки'],
    description='Управление подписками на курсы'
)
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Добавляем проверку аутентификации

    @extend_schema(
        summary='Подписка/отписка от курса',
        description='Добавляет или удаляет подписку пользователя на курс',
        request={
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'course_id': {
                            'type': 'integer',
                            'description': 'ID курса для подписки'
                        }
                    },
                    'required': ['course_id']
                }
            }
        },
        responses={
            201: {
                'description': 'Подписка добавлена',
                'content': {
                    'application/json': {
                        'example': {'message': 'Подписка добавлена'}
                    }
                }
            },
            200: {
                'description': 'Подписка удалена',
                'content': {
                    'application/json': {
                        'example': {'message': 'Подписка удалена'}
                    }
                }
            },
            400: {
                'description': 'Неверный запрос',
                'content': {
                    'application/json': {
                        'example': {'error': 'course_id обязателен'}
                    }
                }
            },
            404: {
                'description': 'Курс не найден'
            }
        }
    )
    def post(self, request):
        """Обработка подписки/отписки пользователя от курса"""
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        course_item = get_object_or_404(Course, id=course_id)
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            course=course_item
        )

        if not created:
            subscription.delete()
            message = 'Подписка удалена'
            status_code = status.HTTP_200_OK
        else:
            message = 'Подписка добавлена'
            status_code = status.HTTP_201_CREATED

        return Response({"message": message}, status=status_code)

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


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Добавляем проверку аутентификации

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

from django.db import models
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.annotate(
        lessons_count=models.Count('lessons')).prefetch_related('lessons')
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'retrieve', 'list']:
            self.permission_classes = [IsAuthenticated | IsModerator]
        return [permission() for permission in self.permission_classes]


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'retrieve', 'list']:
            self.permission_classes = [IsAuthenticated | IsModerator]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        if not self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.filter(owner=self.request.user)
        return Lesson.objects.all()

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, SubscriptionAPIView, LessonViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'lessons', LessonViewSet, basename='lessons')

urlpatterns = [
    path('', include(router.urls)),
    path('subscription/', SubscriptionAPIView.as_view(), name='subscription'),
]

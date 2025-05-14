from django.urls import reverse
from rest_framework import status, serializers
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from users.models import CustomUser as User
from django.contrib.auth.models import Group
from materials.models import Course, Lesson, Subscription
from materials.validators import YouTubeLinkValidator


class YouTubeValidatorTestCase(APITestCase):
    """Тесты валидатора YouTube ссылок (ваши существующие тесты)"""

    def setUp(self):
        self.valid_link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        self.invalid_link = 'https://vk.com/video123'
        self.empty_link = ''

    def test_valid_youtube_link(self):
        validator = YouTubeLinkValidator(field='video_link')
        try:
            validator(self.valid_link)
        except serializers.ValidationError:
            self.fail("Валидатор неожиданно отклонил валидную youtube ссылку")

    def test_invalid_youtube_link(self):
        validator = YouTubeLinkValidator(field='video_link')
        with self.assertRaises(serializers.ValidationError):
            validator(self.invalid_link)

    def test_empty_link(self):
        validator = YouTubeLinkValidator(field='video_link')
        try:
            validator(self.empty_link)
        except serializers.ValidationError:
            self.fail("Валидатор не должен проверять пустые ссылки")


class LessonTestCase(APITestCase):
    """Расширенные тесты для уроков"""

    def setUp(self):
        # Создаем тестовых пользователей
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser'
        )
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123',
            username='moderatoruser'
        )
        moderator_group = Group.objects.create(name='moderators')
        self.moderator.groups.add(moderator_group)

        # Создаем тестовый курс
        self.course = Course.objects.create(
            name='Test Course',
            owner=self.user
        )

        # Тестовые данные
        self.valid_data = {
            'title': 'Valid Lesson',
            'video_link': 'https://youtu.be/dQw4w9WgXcQ',
            'description': 'Valid description',
            'course': self.course.id
        }
        self.invalid_data = {
            'title': 'Invalid Lesson',
            'video_link': 'https://example.com/video',
            'course': self.course.id
        }

    def test_create_lesson_authenticated(self):
        """Авторизованный пользователь может создать урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('lessons-list'),
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(title='Valid Lesson').exists())

    def test_create_lesson_unauthenticated(self):
        """Неавторизованный пользователь не может создать урок"""
        response = self.client.post(
            reverse('lessons-list'),
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_invalid_data(self):
        """Проверка валидации данных при создании урока"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('lessons-list'),
            data=self.invalid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.json())

    def test_update_lesson_as_owner(self):
        """Владелец может обновить урок"""
        lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse('lessons-detail', args=[lesson.id]),
            {'title': 'Updated Lesson'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, 'Updated Lesson')

    def test_delete_lesson_as_moderator(self):
        """Модератор может удалить урок"""
        lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user
        )
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(
            reverse('lessons-detail', args=[lesson.id])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=lesson.id).exists())


class SubscriptionTestCase(APITestCase):
    """Тесты для подписок на курсы"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            username='testuser'
        )
        self.course = Course.objects.create(
            name='Test Course',
            owner=self.user
        )
        self.subscription_url = reverse('subscription')

    def test_create_subscription(self):
        """Пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.subscription_url,
            {'course_id': self.course.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

    def test_delete_subscription(self):
        """Пользователь может отписаться от курса"""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.subscription_url,
            {'course_id': self.course.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Subscription.objects.filter(
            user=self.user,
            course=self.course
        ).exists())

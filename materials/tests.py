from rest_framework import status, serializers
from rest_framework.test import APITestCase

from materials.models import Lesson
from materials.validators import YouTubeLinkValidator


class YouTubeValidatorTestCase(APITestCase):
    def setUp(self):
        self.valid_link = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        self.invalid_link = 'https://vk.com/video123'
        self.empty_link = ''

    def test_valid_youtube_link(self):
        """Тест на валидную youtube ссылку"""
        validator = YouTubeLinkValidator(field='video_link')
        try:
            validator(self.valid_link)
        except serializers.ValidationError:
            self.fail("Валидатор неожиданно отклонил валидную youtube ссылку")

    def test_invalid_youtube_link(self):
        """Тест на невалидную ссылку"""
        validator = YouTubeLinkValidator(field='video_link')
        with self.assertRaises(serializers.ValidationError):
            validator(self.invalid_link)

    def test_empty_link(self):
        """Тест на пустую ссылку"""
        validator = YouTubeLinkValidator(field='video_link')
        try:
            validator(self.empty_link)
        except serializers.ValidationError:
            self.fail("Валидатор не должен проверять пустые ссылки")


class LessonAPITestCase(APITestCase):
    def setUp(self):
        self.valid_data = {
            'title': 'Valid Lesson',
            'video_link': 'https://youtu.be/dQw4w9WgXcQ',
            'description': 'Lesson with valid youtube link'
        }

        self.invalid_data = {
            'title': 'Invalid Lesson',
            'video_link': 'https://example.com/video',
            'description': 'Lesson with invalid link'
        }

    def test_create_lesson_with_valid_link(self):
        """Тест создания урока с валидной youtube ссылкой"""
        response = self.client.post(
            '/lessons/',
            data=self.valid_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Lesson.objects.filter(title='Valid Lesson').exists()
        )

    def test_create_lesson_with_invalid_link(self):
        """Тест создания урока с невалидной ссылкой"""
        response = self.client.post(
            '/lessons/',
            data=self.invalid_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'video_link',
            response.json()
        )

        self.assertEqual(
            response.json()['video_link'],
            ["Ссылка в поле 'video_link' должна вести на youtube.com"]
        )

        self.assertFalse(
            Lesson.objects.filter(title='Invalid Lesson').exists()
        )
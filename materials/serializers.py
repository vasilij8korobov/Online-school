
from rest_framework import serializers
from .models import Course, Lesson
from .validators import YouTubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            YouTubeLinkValidator(field='video_link'),
            YouTubeLinkValidator(field='materials_link')
        ]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'name': {'help_text': 'Название курса'},
        }
        validators = [
            YouTubeLinkValidator(field='materials_link')
        ]

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_subscriptions.filter(user=request.user).exists()
        return False

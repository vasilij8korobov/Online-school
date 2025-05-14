from urllib.parse import urlparse
from rest_framework import serializers


class YouTubeLinkValidator:
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if isinstance(value, dict) and self.field in value:
            url = value[self.field]
            if url:  # Проверяем только если URL не пустой
                parsed_url = urlparse(url)
                if parsed_url.netloc not in ['www.youtube.com', 'youtu.be']:
                    raise serializers.ValidationError("Разрешены только ссылки на YouTube")

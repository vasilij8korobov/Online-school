from urllib.parse import urlparse
from rest_framework import serializers


class YouTubeLinkValidator:
    """
    Валидатор для проверки, что ссылка ведет только на youtube.com
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value:  # Проверяем только если значение не пустое
            parsed_url = urlparse(value)
            if parsed_url.netloc not in ['www.youtube.com', 'youtube.com', 'youtu.be']:
                raise serializers.ValidationError(
                    f"Ссылка в поле '{self.field}' должна вести на youtube.com"
                )

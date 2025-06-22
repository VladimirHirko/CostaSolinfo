from rest_framework import serializers
from modeltranslation.utils import get_translation_fields

class BaseTranslationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор, который автоматически добавляет переводы для указанных полей.
    Пример использования:
        class HomepageSerializer(BaseTranslationSerializer):
            translatable_fields = ['title', 'subtitle']
    """
    translatable_fields = []

    class Meta:
        model = None
        fields = []  # будет переопределено в __new__

    def __new__(cls, *args, **kwargs):
        cls.Meta.fields = []
        if cls.Meta.model and hasattr(cls, 'translatable_fields'):
            # Добавляем переводы всех указанных полей
            translated_fields = []
            for field in cls.translatable_fields:
                translated_fields += get_translation_fields(field)
            # Добавляем остальные обычные поля вручную (например, изображения)
            cls.Meta.fields = translated_fields + getattr(cls.Meta, 'extra_fields', [])
        return super().__new__(cls)

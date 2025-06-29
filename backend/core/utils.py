from rest_framework import serializers
from modeltranslation.utils import get_translation_fields
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# ⬇️ Для перевода тем писем
from django.utils.translation import gettext as _


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


# 🔹 Темы писем по шаблону и языку
def get_email_subject(template_name, lang):
    subjects = {
        'transfer_notification': {
            'ru': 'Информация о вашем трансфере',
            'en': 'Transfer Information',
            'es': 'Información sobre su traslado',
            'lv': 'Informācija par jūsu transfēru',
            'lt': 'Informacija apie jūsų pervežimą',
            'et': 'Teave teie transfeeri kohta',
            'uk': 'Інформація про ваш трансфер',
        },
        # Здесь можно добавить другие типы писем
    }

    key = template_name.replace('emails/', '').replace('.html', '').replace(f'_{lang}', '')
    return subjects.get(key, {}).get(lang, subjects.get(key, {}).get('en', 'CostaSolinfo Notification'))


# 🔹 Отправка HTML-письма
def send_html_email(subject, to_email, template_name, context, lang='en'):
    subject = get_email_subject(template_name, lang)
    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Это HTML письмо. Включите отображение HTML в вашем клиенте.",
        from_email="CostaSolinfo.Malaga@gmail.com",
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

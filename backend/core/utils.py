from rest_framework import serializers
from modeltranslation.utils import get_translation_fields
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.conf import settings
from django.urls import reverse
from .models import TransferNotification
# from .email_utils import send_html_email  # или откуда у тебя вызывается send_html_email

# ⬇️ Для перевода тем писем
from django.utils.translation import gettext as _


class BaseTranslationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор, автоматически добавляющий переводы.
    Убираем мусорные поля вроде '_', 'a', 'l'.
    """
    translatable_fields = []
    extra_fields = []

    class Meta:
        model = None
        fields = []

    def __new__(cls, *args, **kwargs):
        # Все реальные поля модели
        valid_fields = {f.name for f in cls.Meta.model._meta.get_fields()} if cls.Meta.model else set()

        translated_fields = []
        if cls.Meta.model and hasattr(cls, 'translatable_fields'):
            for field in cls.translatable_fields:
                candidates = get_translation_fields(field)
                filtered = [f for f in candidates if f in valid_fields]
                translated_fields.extend(filtered)

        meta_extra = getattr(cls.Meta, 'extra_fields', [])
        extra_fields_clean = [f for f in meta_extra if f in valid_fields]

        # Итог: только валидные поля
        cls.Meta.fields = list(set(translated_fields + extra_fields_clean))

        print(f"[DEBUG CLEAN] Итоговые поля сериализатора: {cls.Meta.fields}")

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

def send_transfer_update_email(notification: TransferNotification):
    path = reverse('transfer_confirm', kwargs={"token": notification.confirmation_token})
    confirmation_link = f"{settings.SITE_URL}/api/transfer-confirm/{notification.confirmation_token}/"

    print("[DEBUG] Ссылка подтверждения:", confirmation_link)

    context = {
        'hotel_name': notification.hotel.name,
        'departure_date': notification.departure_date.strftime("%d.%m.%Y"),
        'new_time': notification.departure_time.strftime("%H:%M"),
        'pickup_point': notification.pickup_point.name if notification.pickup_point else None,
        'map_link': notification.map_link,
        'confirmation_link': confirmation_link,
    }

    send_html_email(
        subject="Время трансфера изменено",
        template="emails/transfer_notification_ru.html",
        context=context,
        to=[notification.email]
    )

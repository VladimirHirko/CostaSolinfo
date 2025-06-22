from core.models import Homepage, Excursion, InfoMeeting, AirportTransfer, Question, ContactInfo, AboutUs
from .utils import BaseTranslationSerializer  # путь зависит от твоей структуры проекта

class HomepageSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'subtitle']

    class Meta:
        model = Homepage
        extra_fields = ['banner_image']


class ExcursionSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'description']

    class Meta:
        model = Excursion
        extra_fields = ['price', 'duration', 'image']  # добавь любые доп. поля


class InfoMeetingSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'content', 'location']

    class Meta:
        model = InfoMeeting
        extra_fields = ['date', 'time']  # добавь реальные дополнительные поля, если есть


class AirportTransferSerializer(BaseTranslationSerializer):
    translatable_fields = ['description']

    class Meta:
        model = AirportTransfer
        extra_fields = ['departure_time', 'pickup_location']  # поправь по фактическим полям


class QuestionSerializer(BaseTranslationSerializer):
    translatable_fields = ['message']

    class Meta:
        model = Question
        extra_fields = ['email', 'created_at']  # если есть


class ContactInfoSerializer(BaseTranslationSerializer):
    translatable_fields = ['office_name', 'address']

    class Meta:
        model = ContactInfo
        extra_fields = ['phone', 'email', 'map_link']  # замени на свои


class AboutUsSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'description']

    class Meta:
        model = AboutUs
        extra_fields = ['image']  # если есть



from core.models import (
    Homepage, Excursion, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, TransferSchedule,
    Hotel, PickupPoint
    )

from rest_framework import serializers
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



# Трансферы
class AirportTransferSerializer(BaseTranslationSerializer):
    translatable_fields = ['description', 'pickup_location']

    class Meta:
        model = AirportTransfer
        extra_fields = ['departure_time', 'departure_date', 'contact_email']  # поправь по фактическим полям

class TransferScheduleRequestSerializer(serializers.Serializer):
    transfer_type = serializers.ChoiceField(choices=[('group', 'Group'), ('private', 'Private')])
    hotel_id = serializers.IntegerField()
    departure_date = serializers.DateField()
    passenger_last_name = serializers.CharField(required=False, allow_blank=True)

class TransferScheduleResponseSerializer(serializers.Serializer):
    departure_time = serializers.TimeField()
    pickup_point_name = serializers.CharField()
    pickup_point_lat = serializers.FloatField()
    pickup_point_lng = serializers.FloatField()
    hotel_lat = serializers.FloatField()
    hotel_lng = serializers.FloatField()



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



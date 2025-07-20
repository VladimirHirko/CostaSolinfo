from core.models import (
    Homepage, Excursion, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, TransferSchedule,
    Hotel, PickupPoint, TransferNotification, TransferInquiry,
    PrivacyPolicy, InfoMeetingScheduleItem
    )
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
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
        fields = '__all__'  # обязательно добавить!

class InfoMeetingScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoMeetingScheduleItem
        fields = ['id', 'date', 'time_from', 'time_to']





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

class TransferNotificationCreateSerializer(serializers.ModelSerializer):
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = TransferNotification
        fields = ['email', 'transfer_type', 'hotel', 'departure_date', 'language', 'last_name']

    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError(_("Введите корректный email."))
        return value

    def create(self, validated_data):
        instance, created = TransferNotification.objects.get_or_create(
            email=validated_data['email'],
            hotel=validated_data['hotel'],
            transfer_type=validated_data['transfer_type'],
            departure_date=validated_data['departure_date'],
            language=validated_data.get('language', 'ru'),
            defaults={'last_name': validated_data.get('last_name')}
        )

        # Если объект уже был, но last_name отсутствует — добавим
        if not instance.last_name and validated_data.get('last_name'):
            instance.last_name = validated_data['last_name']
            instance.save(update_fields=["last_name"])

        return instance


# Обратная связь по индивидуальному трансферу
class TransferInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferInquiry
        fields = '__all__'





class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name', 'latitude', 'longitude']

class SimpleHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name']  # можно добавить другие поля, если нужно



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

# Политика конфиденциальности
class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['language_code', 'content']
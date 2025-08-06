from core.models import (
    Homepage, Excursion, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, TransferSchedule,
    Hotel, PickupPoint, TransferNotification, TransferInquiry,
    PrivacyPolicy, InfoMeetingScheduleItem, ExcursionContentBlock,
    PageBanner, ExcursionImage, Question
    )
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers
from .utils import BaseTranslationSerializer  # путь зависит от твоей структуры проекта

class PageBannerSerializer(serializers.ModelSerializer):
    titles = serializers.SerializerMethodField()

    class Meta:
        model = PageBanner
        fields = ["image", "titles"]

    def get_titles(self, obj):
        return {
            "ru": obj.title_ru,
            "en": obj.title_en,
            "es": obj.title_es,
            "uk": obj.title_uk,
            "et": obj.title_et,
            "lv": obj.title_lv,
            "lt": obj.title_lt,
        }

class HomepageSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'subtitle']
    banner_image = serializers.ImageField(use_url=True)

    class Meta:
        model = Homepage
        fields = ['title', 'subtitle', 'banner_image']
        extra_fields = ['banner_image']



class ExcursionContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionContentBlock
        fields = [
            'order',
            'title_ru', 'title_en', 'title_es', 'title_lt', 'title_lv', 'title_et', 'title_uk',
            'content_ru', 'content_en', 'content_es', 'content_lt', 'content_lv', 'content_et', 'content_uk',
        ]


class ExcursionSerializer(serializers.ModelSerializer):
    localized_title = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()

    class Meta:
        model = Excursion
        fields = [
            'id',
            'duration',
            'direction',
            'days',
            'image',
            'localized_title',
            'localized_description',
        ]

    def get_localized_title(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'ru')
        block = obj.content_blocks.filter(block_type='description').first()
        if block:
            return getattr(block, f"title_{lang}", None) or obj.title
        return obj.title

    def get_localized_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'ru')
        block = obj.content_blocks.filter(block_type='description').first()
        if block:
            return getattr(block, f"content_{lang}", None) or block.content or ""
        return ""


class ExcursionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'alt_text']

class ExcursionDetailSerializer(serializers.ModelSerializer):
    images = ExcursionImageSerializer(many=True, read_only=True)
    localized_title = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    content_blocks = serializers.SerializerMethodField()

    class Meta:
        model = Excursion
        fields = '__all__'

    def get_language(self):
        request = self.context.get("request")
        if request:
            return getattr(request, "LANGUAGE_CODE", "ru")
        return "ru"

    def get_localized_title(self, obj):
        lang = self.get_language()
        block = obj.content_blocks.filter(block_type="description").first()
        if block:
            return getattr(block, f"title_{lang}", None) or obj.title
        return obj.title

    def get_localized_description(self, obj):
        lang = self.get_language()
        block = obj.content_blocks.filter(block_type="description").first()
        if block:
            return getattr(block, f"content_{lang}", None) or block.content or ""
        return ""

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(img.image.url) 
            for img in obj.images.all()
        ]

    def get_content_blocks(self, obj):
        lang = self.get_language()
        return [
            {
                "type": block.block_type,
                "localized_title": getattr(block, f"title_{lang}", block.title),
                "localized_content": getattr(block, f"content_{lang}", block.content or "")
            }
            for block in obj.content_blocks.all()
        ]









class InfoMeetingSerializer(BaseTranslationSerializer):
    translatable_fields = ['title', 'content']

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
        fields = ['id', 'name', 'latitude', 'longitude', 'region']


class SimpleHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'name']  # можно добавить другие поля, если нужно



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'



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
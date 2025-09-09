import re
import unicodedata
import logging
from core.models import (
    Homepage, Excursion, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, TransferSchedule,
    Hotel, PickupPoint, TransferNotification, TransferInquiry,
    PrivacyPolicy, InfoMeetingScheduleItem, ExcursionContentBlock,
    PageBanner, ExcursionImage, TeamMember, TransferPageContentBlock,
    ExcursionRules
    )
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers
from .utils import BaseTranslationSerializer  # путь зависит от твоей структуры проекта

logger = logging.getLogger(__name__)
# лид/трейл-очистка с учётом невидимых пробелов
_TRIM_RE = re.compile(r'^[\s\u00A0\u200B\u200C\u200D\uFEFF]+|[\s\u00A0\u200B\u200C\u200D\uFEFF]+$')

SUPPORTED_LANGS = ('ru','en','es','lt','lv','et','uk')


# Правила проведения экскурсий
class ExcursionRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionRules
        fields = ("language_code", "title", "content", "updated_at")
        

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


DAY_CODE_TO_INDEX = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
    # на всякий случай — поддержка полных англ. названий
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    # и русских, если вдруг попадут в БД
    "понедельник": 0, "вторник": 1, "среда": 2, "четверг": 3, "пятница": 4, "суббота": 5, "воскресенье": 6,
    "пн":0,"вт":1,"ср":2,"чт":3,"пт":4,"сб":5,"вс":6,
}

class ExcursionSerializer(serializers.ModelSerializer):
    localized_title = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()
    available_days = serializers.SerializerMethodField()   # [0..6]
    tour_languages = serializers.SerializerMethodField()   # ["en","de",...]

    class Meta:
        model = Excursion
        fields = [
            'id',
            'duration',
            'direction',
            'days',                  # как хранится в БД (список кодов)
            'image',
            'localized_title',
            'localized_description',
            'available_days',        # нормализованный массив индексов для фронта
            'tour_languages',
        ]

    # ===== локализация =====
    def get_localized_title(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'ru')
        block = obj.content_blocks.filter(block_type='description').first()
        if block:
            return getattr(block, f"title_{lang}", None) or getattr(obj, "title", "")
        return getattr(obj, "title", "")

    def get_localized_description(self, obj):
        request = self.context.get('request')
        lang = getattr(request, 'LANGUAGE_CODE', 'ru')
        block = obj.content_blocks.filter(block_type='description').first()
        if block:
            return getattr(block, f"content_{lang}", None) or (block.content or "")
        return ""

    # ===== дни недели → [0..6] =====
    def get_available_days(self, obj):
        v = getattr(obj, "days", None)

        # список кодов: ["mon","wed"]
        if isinstance(v, (list, tuple)):
            out = []
            for token in v:
                key = str(token).strip().lower()
                if key in DAY_CODE_TO_INDEX:
                    out.append(DAY_CODE_TO_INDEX[key])
            return sorted({*out})

        # строка: "mon,wed"
        if isinstance(v, str) and v.strip():
            out = []
            for token in v.replace(";", ",").split(","):
                key = token.strip().lower()
                if key.isdigit():
                    num = int(key)
                    if 0 <= num <= 6:
                        out.append(num)
                elif key in DAY_CODE_TO_INDEX:
                    out.append(DAY_CODE_TO_INDEX[key])
            return sorted({*out})

        # ничего нет
        return []

    # ===== языки экскурсии → ["en","de",...] =====
    def get_tour_languages(self, obj):
        langs = []
        if getattr(obj, "lang_en", False): langs.append("en")
        if getattr(obj, "lang_de", False): langs.append("de")
        if getattr(obj, "lang_es", False): langs.append("es")
        if getattr(obj, "lang_fr", False): langs.append("fr")
        if getattr(obj, "lang_ru", False): langs.append("ru")
        return langs


class ExcursionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcursionImage
        fields = ['id', 'image', 'alt_text']

class ExcursionDetailSerializer(ExcursionSerializer):
    images = serializers.SerializerMethodField()
    content_blocks = serializers.SerializerMethodField()

    class Meta(ExcursionSerializer.Meta):
        # всё из списка + детальные поля
        fields = ExcursionSerializer.Meta.fields + [
            'images',
            'content_blocks',
        ]

    def _lang(self):
        req = self.context.get("request")
        return getattr(req, "LANGUAGE_CODE", "ru")

    def get_images(self, obj):
        req = self.context.get("request")
        out = []
        for im in obj.images.all().order_by('id'):
            url = getattr(im.image, "url", "")
            if not url:
                continue
            if req and not url.startswith("http"):
                url = req.build_absolute_uri(url)
            out.append(url)
        return out

    def get_content_blocks(self, obj):
        lang = self._lang()
        blocks = []
        for b in obj.content_blocks.all().order_by('order', 'id'):
            blocks.append({
                "block_type": b.block_type,  # фронт читает block.block_type || block.type
                "localized_title": getattr(b, f"title_{lang}", None) or (b.title or ""),
                "localized_content": getattr(b, f"content_{lang}", None) or (b.content or ""),
            })
        return blocks



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

class TransferPageContentBlockSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = TransferPageContentBlock
        fields = ('id', 'page', 'order', 'title', 'content')

    def _lang(self):
        req = self.context.get('request')
        q = (req.query_params.get('lang') if req else None) or ''
        h = (req.headers.get('Accept-Language') if req else '') or ''
        lang = (q or h[:2] or 'ru').lower()
        return lang if lang in SUPPORTED_LANGS else 'ru'

    def get_title(self, obj):
        lang = self._lang()
        return getattr(obj, f'title_{lang}', '') or getattr(obj, 'title_ru', '')

    def get_content(self, obj):
        lang = self._lang()
        return getattr(obj, f'content_{lang}', '') or getattr(obj, 'content_ru', '')

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



def _normalize_text(val: str) -> str:
    if val is None:
        return ''
    s = unicodedata.normalize('NFKC', str(val))
    s = s.replace('\u00A0', ' ')
    s = s.replace('\u200B', '').replace('\u200C', '').replace('\u200D', '').replace('\uFEFF', '')
    s = _TRIM_RE.sub('', s)
    s = re.sub(r'\s+', ' ', s)
    return s

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'  # убедись, что 'question' включён и не read_only

    def to_internal_value(self, data):
        raw = None
        picked = None
        for key in ('question', 'message', 'text', 'msg', 'body', 'content'):
            if key in data and data.get(key) is not None:
                raw = data.get(key)
                picked = key
                break
        logger.debug("[QuestionSerializer] picked=%r raw=%r", picked, raw)
        cleaned = _normalize_text(raw if raw is not None else '')
        logger.debug("[QuestionSerializer] cleaned=%r", cleaned)

        mutable = dict(data)
        mutable['question'] = cleaned  # проброс в нужное поле
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        txt = attrs.get('question', '')
        if not any(ch.isalnum() for ch in txt):
            raise serializers.ValidationError({"question": "Please enter a valid message."})
        return attrs

    def create(self, validated_data):
        # ⛑ страховка: создаём явно и проверяем
        qtxt = validated_data.get('question', '')
        instance = Question.objects.create(**validated_data)
        logger.debug("[QuestionSerializer.create] created id=%s question_before=%r", instance.id, instance.question)

        # Если вдруг кто-то обнулил — восстанавливаем
        if not instance.question and qtxt:
            instance.question = qtxt
            instance.save(update_fields=['question'])
            logger.debug("[QuestionSerializer.create] restored question id=%s question_after=%r", instance.id, instance.question)

        return instance


class AskPageContentSerializer(serializers.Serializer):
    title = serializers.CharField()
    content = serializers.CharField()



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

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'position', 'photo', 'email', 'whatsapp']


# Политика конфиденциальности
class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = ['language_code', 'content']
import pandas as pd
import datetime
import math
from django.db.models import Count, F 
from django.db import models, transaction
from django.conf import settings
from math import radians, sin, cos, sqrt, atan2, asin
from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from modeltranslation.admin import TranslationAdmin
from .models import (
    Hotel, Excursion, PickupPoint,
    Homepage, InfoMeeting, AirportTransfer,
    Question, ContactInfo, AboutUs, TransferSchedule,
    Region, PageBanner, GroupTransferPickupPoint, PrivateTransferPickupPoint,
    TransferSchedule, TransferScheduleGroup, TransferNotification,
    TransferInquiry, TransferInquiryLog, TransferScheduleItem,
    TransferChangeLog, PrivacyPolicy, Homepage, InfoMeetingScheduleItem,
    ExcursionPickupPoint, ExcursionRegionPrice, ExcursionContentBlock, 
    ExcursionPickupReference, ExcursionImage, Question, TeamMember,
    TransferPageContentBlock, TransferPassenger, HotelExcursion, ExcursionZone,
    ExcursionRules, AskPageContent
)
from leaflet.admin import LeafletGeoAdmin
from leaflet.forms.widgets import LeafletWidget
from django import forms
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import now, localtime, make_aware
from django.utils.translation import activate, deactivate_all, gettext as _
from core.utils import send_html_email, send_answer_notification
from .forms import ExcursionAdminForm, BulkTransferScheduleForm, ExcursionPickupPointForm

import io, csv
from datetime import datetime, time

try:
    import pandas as pd
except Exception:
    pd = None


# Правила проведения экскурсий
@admin.register(ExcursionRules)
class ExcursionRulesAdmin(admin.ModelAdmin):
    list_display = ("language_code", "title", "updated_at")
    search_fields = ("title", "content")
    list_filter = ("language_code",)


# Баннеры на старницах
@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    list_display = ('page', 'title_en')  # Показываем страницу и заголовок
    search_fields = ('page', 'title_en', 'title_ru')

# === Главная страница ===
class HomepageAdminForm(forms.ModelForm):
    class Meta:
        model = Homepage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ровно как в блоках: все subtitle_* рендерим CKEditor'ом
        for name in self.fields.keys():
            if name.startswith('subtitle'):
                self.fields[name].widget = CKEditorWidget()  # без лишних конфигов, как у тебя в блоках

@admin.register(Homepage)
class HomepageAdmin(TranslationAdmin):  # ключевое отличие
    form = HomepageAdminForm
    list_display = ('title',)

    # «сырое» сохранение HTML — как в блоках
    def save_model(self, request, obj, form, change):
        for key, val in request.POST.items():
            if key == 'subtitle' or key.startswith('subtitle_'):
                setattr(obj, key, val)
        super().save_model(request, obj, form, change)



# Инфо встреча
class InfoMeetingAdminForm(forms.ModelForm):
    class Meta:
        model = InfoMeeting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # навесим CKEditor на все поля контента (content, content_ru, content_en, ...)
        for name in list(self.fields.keys()):
            if name == 'content' or name.startswith('content_'):
                self.fields[name].widget = CKEditorWidget(config_name='default')

@admin.register(InfoMeeting)
class InfoMeetingAdmin(TranslationAdmin):
    form = InfoMeetingAdminForm
    list_display = ('title', 'location', 'date')

    # как делали для Экскурсий/Homepage: сохраняем "сырое" HTML напрямую
    def save_model(self, request, obj, form, change):
        lang_codes = [code for code, _ in getattr(settings, 'LANGUAGES', (('ru','Russian'),))]
        # собираем все потенциальные имена полей контента
        field_names = ['content'] + [f'content_{code}' for code in lang_codes]
        for fname in field_names:
            if fname in request.POST:
                setattr(obj, fname, request.POST.get(fname, ''))
        super().save_model(request, obj, form, change)

class InfoMeetingScheduleInline(admin.TabularInline):
    model = InfoMeetingScheduleItem
    extra = 1  # Кол-во пустых строк для добавления по умолчанию
    fields = ['date', 'time_from', 'time_to']
    ordering = ['date', 'time_from']

@admin.register(InfoMeetingScheduleItem)
class InfoMeetingScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'date', 'time_from', 'time_to')
    list_filter = ('hotel', 'date')




# Трансфер в аэропорт
@admin.register(AirportTransfer)
class AirportTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'departure_date', 'departure_time', 'contact_email']

class TransferPageContentBlockForm(forms.ModelForm):
    class Meta:
        model = TransferPageContentBlock
        fields = '__all__'
        widgets = {
            'content_ru': CKEditorWidget(),
            'content_en': CKEditorWidget(),
            'content_es': CKEditorWidget(),
            'content_lt': CKEditorWidget(),
            'content_lv': CKEditorWidget(),
            'content_et': CKEditorWidget(),
            'content_uk': CKEditorWidget(),
        }

@admin.register(TransferPageContentBlock)
class TransferPageContentBlockAdmin(admin.ModelAdmin):
    form = TransferPageContentBlockForm
    list_display = ('page', 'order', 'title_ru', 'is_active', 'updated_at')
    list_filter = ('page', 'is_active')
    search_fields = ('title_ru', 'title_en', 'title_es')
    ordering = ('page', 'order')

# Задать вопрос
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "category", "source_badge", "language_with_flag", "created_at", "question_short")
    list_filter = ("category", "source", "language", "created_at")  # ✅ фильтр по источнику
    search_fields = ("name", "email", "question")
    date_hierarchy = "created_at"

    # делаем все входящие поля только для чтения, кроме ответа
    readonly_fields = ("name", "email", "hotel", "category", "language", "source", "question", "created_at")
    fields = ("name", "email", "hotel", "category", "language", "source", "question", "answer", "created_at")

    def question_short(self, obj):
        return (obj.question or "—")[:80]
    question_short.short_description = "Текст (превью)"

    def language_with_flag(self, obj):
        from django.utils.html import format_html
        flags = {
            'ru': '🇷🇺', 'en': '🇬🇧', 'es': '🇪🇸',
            'lt': '🇱🇹', 'lv': '🇱🇻', 'et': '🇪🇪', 'uk': '🇺🇦'
        }
        return format_html('{}&nbsp;{}', flags.get(obj.language, ''), obj.get_language_display())
    language_with_flag.short_description = 'Язык'

    def source_badge(self, obj):
        from django.utils.html import format_html
        labels = {'ask': 'Задать вопрос', 'contacts': 'Контакты'}
        bg = {'ask': '#eef6ff', 'contacts': '#e8fff3'}
        border = {'ask': '#cfe6ff', 'contacts': '#bcecd3'}
        return format_html(
            '<span style="padding:3px 8px;border-radius:10px;'
            'background:{};border:1px solid {};font-size:12px;">{}</span>',
            bg.get(obj.source, '#f7f7f7'),
            border.get(obj.source, '#eaeaea'),
            labels.get(obj.source, obj.source),
        )
    source_badge.short_description = "Источник"

    def save_model(self, request, obj, form, change):
        if not obj.question:
            obj.question = form.initial.get('question')

        send_email = False
        if 'answer' in form.changed_data and obj.answer:
            send_email = True
        super().save_model(request, obj, form, change)
        if send_email:
            send_answer_notification(obj)


class AskPageContentAdminForm(forms.ModelForm):
    class Meta:
        model = AskPageContent
        fields = "__all__"
        # тот же CKEditor, что ты уже используешь в политике приватности
        widgets = {
            "content_ru": CKEditorWidget(), "content_en": CKEditorWidget(),
            "content_es": CKEditorWidget(), "content_uk": CKEditorWidget(),
            "content_lt": CKEditorWidget(), "content_lv": CKEditorWidget(),
            "content_et": CKEditorWidget(),
        }

@admin.register(AskPageContent)
class AskPageContentAdmin(admin.ModelAdmin):
    form = AskPageContentAdminForm
    list_display = ("updated_at",)
    # делаем модель «синглтоном»: одна запись на сайт
    def has_add_permission(self, request):
        if AskPageContent.objects.exists():
            return False
        return super().has_add_permission(request)



# Контакты
@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'email', 'phone', 'whatsapp')

#О нас
@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'whatsapp', 'order')
    ordering = ('order',)


class PrivacyPolicyAdminForm(forms.ModelForm):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'
        widgets = {
            'content': CKEditorWidget(),
        }

# Политика конфиденциальности
@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('language_code',)
    ordering = ('language_code',)
    form = PrivacyPolicyAdminForm

# Точки сбора по трансферам
class PickupPointInline(admin.TabularInline):
    model = PickupPoint
    extra = 1
    fields = ('name', 'transfer_type', 'latitude', 'longitude', 'location_description')
    verbose_name = "Точка сбора"
    verbose_name_plural = "Точки сбора"


@admin.register(ExcursionZone)
class ExcursionZoneAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


class HotelExcursionInline(admin.TabularInline):
    model = HotelExcursion
    extra = 0
    fields = ('excursion', 'is_active')
    autocomplete_fields = ('excursion',)

# Админка отели
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "excursion_zone")
    list_filter  = ("region", "excursion_zone")
    search_fields = ['name']
    fields = ("name", "region", "excursion_zone", "latitude", "longitude")  # ❗ pickup_point убираем
    inlines = [PickupPointInline, InfoMeetingScheduleInline, HotelExcursionInline]  # 🆕 добавлен Inline
    readonly_fields = ()

    class Media:
        js = (
            "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js",
        )
        css = {
            "all": (
                "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css",
                "admin/css/admin_custom.css",
            )
        }

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['map_html'] = mark_safe(f'''
            <div style="margin-top:20px; width:100%;">
                <h3 style="margin-bottom: 5px;">Выбор координат на карте</h3>
                <div id="map" style="height: 500px; width: 100%; border: 1px solid #ccc;"></div>
                <script>
                    setTimeout(function() {{
                        var latInput = document.getElementById('id_latitude');
                        var lngInput = document.getElementById('id_longitude');
                        var lat = parseFloat(latInput.value) || 36.595;
                        var lng = parseFloat(lngInput.value) || -4.537;
                        var map = L.map('map').setView([lat, lng], 13);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: 'Map data © OpenStreetMap contributors'
                        }}).addTo(map);
                        var marker = L.marker([lat, lng], {{draggable: true}}).addTo(map);
                        marker.on('dragend', function(e) {{
                            var coords = e.target.getLatLng();
                            latInput.value = coords.lat.toFixed(6);
                            lngInput.value = coords.lng.toFixed(6);
                        }});
                        map.on('click', function(e) {{
                            marker.setLatLng(e.latlng);
                            latInput.value = e.latlng.lat.toFixed(6);
                            lngInput.value = e.latlng.lng.toFixed(6);
                        }});
                    }}, 500);
                </script>
            </div>
        ''')
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

class ExcursionHotelInline(admin.TabularInline):
    model = HotelExcursion
    extra = 0
    fields = ('hotel', 'is_active')
    autocomplete_fields = ('hotel',)

# Админка для регионов
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']  # 👈 добавляем


class ExcursionPickupInline(admin.TabularInline):
    model = ExcursionPickupPoint
    extra = 1
    autocomplete_fields = ['hotel', 'copy_from']
    fields = (
        'hotel', 'copy_from', 'pickup_point_name', 'pickup_time',
        'latitude', 'longitude', 'get_direction', 'get_price_adult', 'get_price_child'
    )
    readonly_fields = (
        'pickup_point_name', 'latitude', 'longitude',
        'get_direction', 'get_price_adult', 'get_price_child'
    )
    # базовая сортировка (на случай старых версий Django)
    ordering = ("pickup_time", "hotel__name", "pickup_point_name")

    # корректно уводим пустые времена вниз (Django 3.1+)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            return qs.order_by(
                F("pickup_time").asc(nulls_last=True),
                "hotel__name",
                "pickup_point_name",
            )
        except TypeError:
            return qs.order_by("pickup_time", "hotel__name", "pickup_point_name")

    def get_direction(self, obj):
        return obj.direction
    get_direction.short_description = "Направление"

    def get_price_adult(self, obj):
        return obj.price_adult
    get_price_adult.short_description = "Цена взрослый"

    def get_price_child(self, obj):
        return obj.price_child
    get_price_child.short_description = "Цена ребёнок"

@admin.register(ExcursionPickupReference)
class ExcursionPickupReferenceAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'latitude', 'longitude', 'default_time']


class ExcursionPickupPointForm(forms.ModelForm):
    class Meta:
        model = ExcursionPickupPoint
        fields = '__all__'
        ordering = ["pickup_time", "hotel__name", "pickup_point_name"]

    def clean(self):
        cleaned_data = super().clean()
        excursion = cleaned_data.get("excursion")
        hotel = cleaned_data.get("hotel")
        pickup_point = cleaned_data.get("pickup_point")

        # === Автозаполнение по выбранной точке сбора ===
        if pickup_point:
            cleaned_data["pickup_point_name"] = pickup_point.name
            cleaned_data["latitude"] = pickup_point.latitude
            cleaned_data["longitude"] = pickup_point.longitude
            if not cleaned_data.get("pickup_time"):
                cleaned_data["pickup_time"] = getattr(pickup_point, "default_time", None)

        # === Цены по региону ===
        if excursion and hotel and hotel.region:
            try:
                region_price = ExcursionRegionPrice.objects.get(
                    excursion=excursion,
                    region=hotel.region
                )
                cleaned_data["price_adult"] = region_price.price_adult
                cleaned_data["price_child"] = region_price.price_child
            except ExcursionRegionPrice.DoesNotExist:
                self.add_error("hotel", f"Для региона {hotel.region} не установлены цены")

        return cleaned_data



@admin.action(description="Санитарная уборка: удалить без отеля и склеить дубли")
def cleanup_pickups(modeladmin, request, queryset):
    # игнорируем queryset — чистим глобально
    orph = ExcursionPickupPoint.objects.filter(hotel__isnull=True)
    n_orph = orph.count()
    orph.delete()

    dups = (ExcursionPickupPoint.objects
            .values('excursion_id', 'hotel_id')
            .annotate(c=Count('id')).filter(c__gt=1))
    removed = 0
    for row in dups:
        items = list(ExcursionPickupPoint.objects
                     .filter(excursion_id=row['excursion_id'], hotel_id=row['hotel_id'])
                     .order_by('-pickup_time', '-id'))
        keep = items[0]
        for x in items[1:]:
            updated = False
            if not keep.pickup_time and x.pickup_time:
                keep.pickup_time = x.pickup_time; updated = True
            if keep.latitude is None and x.latitude is not None:
                keep.latitude = x.latitude; updated = True
            if keep.longitude is None and x.longitude is not None:
                keep.longitude = x.longitude; updated = True
            if not keep.pickup_point_name and x.pickup_point_name:
                keep.pickup_point_name = x.pickup_point_name; updated = True
            if updated:
                keep.save()
            x.delete()
            removed += 1

    modeladmin.message_user(
        request, f"Удалено без отеля: {n_orph}, удалено дублей: {removed}"
    )

@admin.register(ExcursionPickupPoint)
class ExcursionPickupPointAdmin(admin.ModelAdmin):
    change_list_template = "admin/core/excursionpickuppoint/change_list.html"  # ← добавили
    form = ExcursionPickupPointForm
    search_fields = ['pickup_point_name']
    list_display = ('id', 'get_hotel', 'get_excursion', 'pickup_time', 'get_region')
    fields = ('excursion', 'hotel', 'pickup_point_name', 'pickup_time', 'latitude', 'longitude', 'map_block')
    readonly_fields = ('map_block',)
    actions = [cleanup_pickups]

    # По желанию — скрыть «без отеля» в списке:
    def get_queryset(self, request):
        qs = super().get_queryset(request).filter(hotel__isnull=False)
        try:
            return qs.order_by(F("pickup_time").asc(nulls_last=True), "hotel__name")
        except TypeError:
            return qs.order_by("pickup_time", "hotel__name")

    def get_hotel(self, obj):
        return obj.hotel.name if obj.hotel else "—"
    get_hotel.short_description = "Отель"

    def get_excursion(self, obj):
        return obj.excursion.title if obj.excursion else "—"
    get_excursion.short_description = "Экскурсия"

    def get_region(self, obj):
        return obj.hotel.region.name if obj.hotel and obj.hotel.region else "—"
    get_region.short_description = "Регион"

    def map_block(self, obj=None):
        return mark_safe(f"""
            <div style="margin-top:20px; width:100%;">
                <h3 style="margin-bottom: 5px;">Выбор координат на карте</h3>
                <div id="map" style="height: 400px; width: 425%; border: 1px solid #ccc;"></div>
                <script>
                    document.addEventListener("DOMContentLoaded", function() {{
                        var latInput = document.getElementById('id_latitude');
                        var lngInput = document.getElementById('id_longitude');
                        var lat = parseFloat(latInput.value) || 36.595;
                        var lng = parseFloat(lngInput.value) || -4.537;

                        var map = L.map('map').setView([lat, lng], 12);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: 'Map data © OpenStreetMap contributors'
                        }}).addTo(map);

                        var marker = L.marker([lat, lng], {{draggable: true}}).addTo(map);

                        marker.on('dragend', function(e) {{
                            var coords = e.target.getLatLng();
                            latInput.value = coords.lat.toFixed(6);
                            lngInput.value = coords.lng.toFixed(6);
                        }});

                        map.on('click', function(e) {{
                            marker.setLatLng(e.latlng);
                            latInput.value = e.latlng.lat.toFixed(6);
                            lngInput.value = e.latlng.lng.toFixed(6);
                        }});
                    }});
                </script>
            </div>
        """)
    map_block.short_description = "Карта выбора точки"

    class Media:
        css = {
            "all": ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"]
        }
        js = ["https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"]

    # 🔹 ДОБАВЛЯЕМ ИМПОРТ и скачку шаблона
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("import/", self.admin_site.admin_view(import_excursion_pickups_view), name="excursion-pickup-import"),
            path("download-template/", self.admin_site.admin_view(download_excursion_template_view), name="excursion-pickup-template"),
        ]
        return custom + urls



class ExcursionRegionPriceInline(admin.TabularInline):
    model = ExcursionRegionPrice
    extra = 1
    autocomplete_fields = ['region']
    fields = ('region', 'price_adult', 'price_child')
    ordering = ['region']
    verbose_name = "Цена по региону"
    verbose_name_plural = "Цены по регионам"


class ExcursionContentBlockForm(forms.ModelForm):
    class Meta:
        model = ExcursionContentBlock
        # Базовые (непереводные) скрываем, работаем только с *_ru, *_en ...
        exclude = ('title', 'content',)
        widgets = {
            'content_ru': CKEditorWidget(),
            'content_en': CKEditorWidget(),
            'content_es': CKEditorWidget(),
            'content_lt': CKEditorWidget(),
            'content_lv': CKEditorWidget(),
            'content_et': CKEditorWidget(),
            'content_uk': CKEditorWidget(),
        }

@admin.register(ExcursionContentBlock)
class ExcursionContentBlockAdmin(admin.ModelAdmin):
    form = ExcursionContentBlockForm
    list_display = ('excursion', 'block_type', 'order', 'title_ru')
    list_filter = ('excursion', 'block_type')
    search_fields = ('title_ru', 'title_en', 'title_es')
    ordering = ['excursion', 'order']

    # «Сырое» сохранение, чтобы CKEditor HTML не чистился
    def save_model(self, request, obj, form, change):
        for key, val in request.POST.items():
            if key.startswith('content_') or key.startswith('title_'):
                setattr(obj, key, val)
        super().save_model(request, obj, form, change)


class ExcursionImageInline(admin.TabularInline):
    model = ExcursionImage
    extra = 1  # сколько пустых полей показывать по умолчанию
    fields = ('image', 'alt_text')

@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    form = ExcursionAdminForm
    list_display = ('title', 'direction', 'duration', 'is_active')
    list_filter = ('direction',)
    search_fields = ('title',)
    inlines = [ExcursionRegionPriceInline, ExcursionPickupInline, ExcursionImageInline, ExcursionHotelInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'duration', 'direction', 'days', 'is_active')
        }),
        ('Фото и медиа', {
            'fields': ('image',)
        }),
        # ⬇️ УБРАЛИ monday..sunday, оставили только days
        
        ("Языки проведения", {
            "fields": ("lang_en","lang_de","lang_es","lang_fr","lang_ru")
        }),
    )

    class Media:
        js = ("admin/js/excursion_pickup_autofill.js",)



# Админка выставления времени и даты на трансферы
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("bulk-transfer-schedule/", self.admin_view(self.bulk_transfer_schedule_view), name="bulk_transfer_schedule"),
        ]
        return custom_urls + urls

    def bulk_transfer_schedule_view(self, request):
        if request.method == 'POST':
            form = BulkTransferScheduleForm(request.POST)
            if form.is_valid():
                transfer_type = form.cleaned_data['transfer_type']
                transfer_date = form.cleaned_data['transfer_date']

                count = 0
                for hotel in Hotel.objects.all():
                    time_field = form.cleaned_data.get(f"time_{hotel.id}")
                    passenger_last_name = form.cleaned_data.get(f"lastname_{hotel.id}")
                    
                    if time_field:
                        pickup_point = PickupPoint.objects.filter(hotel=hotel, transfer_type=transfer_type).first()
                        TransferSchedule.objects.create(
                            transfer_type=transfer_type,
                            hotel=hotel,
                            departure_date=transfer_date,
                            departure_time=time_field,
                            pickup_point=pickup_point,
                            passenger_last_name=passenger_last_name  # 🔹 добавлено
                        )
                        count += 1


                messages.success(request, f"Сохранено {count} трансферов.")
                return redirect("..")

        else:
            form = BulkTransferScheduleForm()

        return render(request, "admin/bulk_transfer_schedule.html", {"form": form})

# Админка точек сбора
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ('region',)  # ❗️это уберёт поле из формы
    list_display = ('name', 'latitude', 'longitude', 'transfer_type')
    list_filter = ('transfer_type',)
    autocomplete_fields = ['hotel']

    class Media:
        js = [
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/pickup_point_map.js',
        ]
        css = {
            'all': ['https://unpkg.com/leaflet@1.9.4/dist/leaflet.css']
        }

# Групповой трансфер
@admin.register(GroupTransferPickupPoint)
class GroupPickupPointAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ('region', 'transfer_type',)
    list_display = ('name', 'hotel', 'latitude', 'longitude')
    list_filter = ('hotel',)
    autocomplete_fields = ['hotel']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(transfer_type='group')

    def save_model(self, request, obj, form, change):
        obj.transfer_type = 'group'
        super().save_model(request, obj, form, change)

    class Media:
        js = [
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/pickup_point_map.js',
        ]
        css = {
            'all': ['https://unpkg.com/leaflet@1.9.4/dist/leaflet.css']
        }


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['map_html'] = mark_safe(f'''
            <div style="margin-top:20px; width:100%;">
                <h3 style="margin-bottom: 5px;">Укажите точку сбора на карте</h3>
                <div id="map" style="height: 500px; width: 100%; border: 1px solid #ccc;"></div>
                <script>
                    setTimeout(function() {{
                        var latInput = document.getElementById('id_latitude');
                        var lngInput = document.getElementById('id_longitude');
                        var lat = parseFloat(latInput.value) || 36.595;
                        var lng = parseFloat(lngInput.value) || -4.537;
                        var map = L.map('map').setView([lat, lng], 13);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: 'Map data © OpenStreetMap contributors'
                        }}).addTo(map);
                        var marker = L.marker([lat, lng], {{draggable: true}}).addTo(map);
                        marker.on('dragend', function(e) {{
                            var coords = e.target.getLatLng();
                            latInput.value = coords.lat.toFixed(6);
                            lngInput.value = coords.lng.toFixed(6);
                        }});
                        map.on('click', function(e) {{
                            marker.setLatLng(e.latlng);
                            latInput.value = e.latlng.lat.toFixed(6);
                            lngInput.value = e.latlng.lng.toFixed(6);
                        }});
                    }}, 500);
                </script>
            </div>
        ''')
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)



# Индивидуальный трансфер
@admin.register(PrivateTransferPickupPoint)
class PrivatePickupPointAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ('region', 'transfer_type',)
    list_display = ('name', 'hotel', 'latitude', 'longitude')
    list_filter = ('hotel',)
    autocomplete_fields = ['hotel']

    def get_queryset(self, request):
        return super().get_queryset(request).filter(transfer_type='private')

    def save_model(self, request, obj, form, change):
        obj.transfer_type = 'private'
        super().save_model(request, obj, form, change)

    class Media:
        js = [
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/pickup_point_map.js',
        ]
        css = {
            'all': ['https://unpkg.com/leaflet@1.9.4/dist/leaflet.css']
        }


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['map_html'] = mark_safe(f'''
            <div style="margin-top:20px; width:100%;">
                <h3 style="margin-bottom: 5px;">Укажите точку сбора на карте</h3>
                <div id="map" style="height: 500px; width: 100%; border: 1px solid #ccc;"></div>
                <script>
                    setTimeout(function() {{
                        var latInput = document.getElementById('id_latitude');
                        var lngInput = document.getElementById('id_longitude');
                        var lat = parseFloat(latInput.value) || 36.595;
                        var lng = parseFloat(lngInput.value) || -4.537;
                        var map = L.map('map').setView([lat, lng], 13);
                        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                            attribution: 'Map data © OpenStreetMap contributors'
                        }}).addTo(map);
                        var marker = L.marker([lat, lng], {{draggable: true}}).addTo(map);
                        marker.on('dragend', function(e) {{
                            var coords = e.target.getLatLng();
                            latInput.value = coords.lat.toFixed(6);
                            lngInput.value = coords.lng.toFixed(6);
                        }});
                        map.on('click', function(e) {{
                            marker.setLatLng(e.latlng);
                            latInput.value = e.latlng.lat.toFixed(6);
                            lngInput.value = e.latlng.lng.toFixed(6);
                        }});
                    }}, 500);
                </script>
            </div>
        ''')
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)


class TransferPassengerInline(admin.TabularInline):
    model = TransferPassenger
    extra = 0

@admin.register(TransferSchedule)
class TransferScheduleAdmin(admin.ModelAdmin):
    list_display = ("transfer_type","booking_service_number","hotel","departure_date","departure_time")
    list_filter  = ("transfer_type","departure_date","hotel")
    search_fields = ("booking_service_number","hotel__name","passengers__last_name","passengers__first_name")
    inlines = [TransferPassengerInline]


class TransferScheduleItemInline(admin.TabularInline):
    model = TransferSchedule
    extra = 0
    autocomplete_fields = ("hotel", "pickup_point")
    show_change_link = True  # ← появится иконка-ссылка "карандаш" к самой записи

    fields = (
        "hotel", "departure_date", "departure_time",
        "pickup_point", "booking_service_number",
        "passenger_list",    # ← показываем фамилии семьи
    )
    readonly_fields = ("passenger_list",)

    def passenger_list(self, obj):
        if not obj.pk:
            return "—"
        names = [f"{p.last_name} {p.first_name}".strip() for p in obj.passengers.all()]
        return ", ".join(names) if names else "—"
    passenger_list.short_description = "Пассажиры (фамилии)"
    

@admin.register(TransferScheduleGroup)
class TransferScheduleGroupAdmin(admin.ModelAdmin):
    inlines = [TransferScheduleItemInline]

    # ⬇⬇⬇ ДОБАВЛЕНО: кнопка «Импорт» на списке групп
    change_list_template = "admin/core/transferschedulegroup/change_list.html"

    def get_urls(self):
        return [
            path("import/", self.admin_site.admin_view(self.import_view),
                 name="core_transferschedulegroup_import"),
        ] + super().get_urls()

    # ==========================
    # ========== ИМПОРТ =========
    # ==========================

    def _parse_date(self, v):
        if v is None or str(v).strip() == "":
            return None
        # pandas.Timestamp или datetime
        if isinstance(v, datetime):
            return v.date()
        # excel-числа (встречается в xlsx)
        if isinstance(v, (int, float)):
            try:
                # pandas есть выше; но тут сделаем без него:
                # 1899-12-30 — базовая дата Excel (Windows)
                base = datetime(1899, 12, 30)
                return (base + timedelta(days=int(v))).date()
            except Exception:
                pass
        # строки в разных форматах
        s = str(v).strip()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                pass
        return None

    def _find_hotel(self, name):
        if not name:
            return None
        name = str(name).strip()
        h = Hotel.objects.filter(name__iexact=name).first()
        return h or Hotel.objects.filter(name__icontains=name).first()

    def _read_table(self, fobj, fname):
        """
        Читает Excel/CSV и находит строку заголовков (ищет 'Номер услуги'/'Номер заявки').
        Возвращает DataFrame с нормальными заголовками.
        """
        if fname.endswith(".xlsx"):
            if not pd:
                raise RuntimeError("Для .xlsx нужен pandas (pip install pandas openpyxl).")
            df_raw = pd.read_excel(fobj, header=None)
        else:
            text = fobj.read().decode("utf-8")
            reader = list(csv.reader(io.StringIO(text)))
            import pandas as _pd
            df_raw = _pd.DataFrame(reader)

        header_row = None
        for i in range(min(30, len(df_raw))):
            row_vals = [str(x) for x in list(df_raw.iloc[i].values)]
            if any(v.startswith("Номер услуги") or v.startswith("Номер заявки") for v in row_vals):
                header_row = i
                break
        if header_row is None:
            # fallback: вдруг сразу корректная шапка
            header_row = 0

        # перечитываем с корректной шапкой
        if fname.endswith(".xlsx"):
            fobj.seek(0)
            df = pd.read_excel(fobj, header=header_row)
        else:
            df = pd.read_csv(io.StringIO(text), header=header_row)

        # нормализуем имена колонок (без lower(), т.к. у нас русские заголовки)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def import_view(self, request):
        if request.method == "POST" and request.FILES.get("file"):
            up = request.FILES["file"]
            name = up.name.lower()

            try:
                df = self._read_table(up, name)

                # обязательные колонки из твоего файла:
                required = {"Отель", "Дата отъезда", "Тип трансфера"}
                if not required.issubset(set(df.columns)):
                    raise RuntimeError(f"В файле должны быть колонки: {', '.join(sorted(required))}")

                created = updated = skipped = errors = 0
                log = []

                rows = []

                # --- PRIVATE: группировка по номеру услуги (семья одной строкой) ---
                priv_mask = df["Тип трансфера"].astype(str).str.upper().isin(["I", "PRIVATE", "ИНДИВИДУАЛЬНЫЙ"])
                priv_df = df[priv_mask]
                if not priv_df.empty:
                    if "Номер услуги" not in df.columns:
                        raise RuntimeError("Для индивидуальных нужен столбец 'Номер услуги'.")

                    gb = priv_df.groupby(["Номер услуги", "Отель", "Дата отъезда"], dropna=False)
                    for (service, hotel_name, dep_date), grp in gb:
                        dep = self._parse_date(dep_date)
                        passengers = []
                        for _, r in grp.iterrows():
                            last_name = str(r.get("Фамилия") or "").strip()
                            first_name = str(r.get("Имя") or "").strip()
                            birth_date = self._parse_date(r.get("Дата рождения"))
                            if last_name:
                                passengers.append(dict(
                                    last_name=last_name,
                                    first_name=first_name,
                                    birth_date=birth_date
                                ))

                        rows.append(dict(
                            transfer_type="private",
                            hotel_name=hotel_name,
                            dep_date=dep,
                            booking_service_number=str(service).strip(),
                            passengers=passengers
                        ))

                # --- GROUP: одна строка на (Отель, Дата отъезда) ---
                grp_mask = df["Тип трансфера"].astype(str).str.upper().isin(["G", "GROUP", "ГРУППОВОЙ"])
                grp_df = df[grp_mask]
                if not grp_df.empty:
                    gb2 = grp_df.groupby(["Отель", "Дата отъезда"], dropna=False)
                    for (hotel_name, dep_date), _grp in gb2:
                        dep = self._parse_date(dep_date)
                        rows.append(dict(
                            transfer_type="group",
                            hotel_name=hotel_name,
                            dep_date=dep,
                            booking_service_number="",   # для группового не нужен
                            passengers=[]
                        ))

                # --- СОЗДАНИЕ/ОБНОВЛЕНИЕ ---
                for r in rows:
                    try:
                        ttype = r["transfer_type"]
                        date = r["dep_date"]
                        hotel = self._find_hotel(r["hotel_name"])

                        if not ttype or not date or not hotel:
                            skipped += 1
                            log.append(f"SKIP: ttype={ttype}, date={date}, hotel={r['hotel_name']!r}")
                            continue

                        with transaction.atomic():
                            group, _ = TransferScheduleGroup.objects.get_or_create(
                                date=date, transfer_type=ttype
                            )

                            if ttype == "private":
                                # одна запись на семью (по номеру услуги)
                                sched, created_flag = TransferSchedule.objects.get_or_create(
                                    group=group,
                                    hotel=hotel,
                                    departure_date=date,
                                    booking_service_number=r.get("booking_service_number", ""),
                                    defaults=dict(
                                        transfer_type="private",
                                        departure_time=None,        # время заполнишь позже
                                        passenger_last_name="",     # не используем для поиска
                                        pickup_point=None,          # подтянется в save() из hotel.pickup_point
                                    )
                                )

                                # добавим всех пассажиров (фамилии/имена)
                                existing = {(p.last_name, p.first_name) for p in sched.passengers.all()}
                                for p in r.get("passengers", []):
                                    key = (p["last_name"], p["first_name"])
                                    if p["last_name"] and key not in existing:
                                        TransferPassenger.objects.create(
                                            schedule=sched,
                                            last_name=p["last_name"],
                                            first_name=p["first_name"],
                                            birth_date=p.get("birth_date"),
                                        )

                                if created_flag:
                                    created += 1
                                    log.append(f"CREATE: {sched}")
                                else:
                                    updated += 1
                                    log.append(f"UPDATE: {sched}")

                            else:
                                # group: одна строка на (отель, дата)
                                qs = TransferSchedule.objects.filter(
                                    group=group, hotel=hotel,
                                    departure_date=date,
                                    transfer_type="group"
                                )
                                if qs.exists():
                                    obj = qs.first()
                                    updated += 1
                                    log.append(f"UPDATE: {obj}")
                                else:
                                    obj = TransferSchedule.objects.create(
                                        group=group,
                                        transfer_type="group",
                                        hotel=hotel,
                                        departure_date=date,
                                        departure_time=None,
                                        passenger_last_name="",
                                        pickup_point=None,
                                    )
                                    created += 1
                                    log.append(f"CREATE: {obj}")

                    except Exception as e:
                        errors += 1
                        log.append(f"ERROR: {e}")

                messages.success(
                    request,
                    f"Импорт: создано {created}, обновлено {updated}, пропущено {skipped}, ошибок {errors}."
                )
                for line in log[:15]:
                    messages.info(request, line)
                if len(log) > 15:
                    messages.info(request, f"...и ещё {len(log)-15} строк лога")

            except Exception as e:
                messages.error(request, f"Ошибка импорта: {e}")

            return redirect("admin:core_transferschedulegroup_changelist")

        # GET — форма загрузки
        ctx = dict(self.admin_site.each_context(request))
        return render(request, "admin/core/transferschedulegroup/import.html", ctx)

    # ==========================
    # ========== SAVE ==========
    # ==========================

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            old_time = None

            if instance.pk:
                try:
                    old = TransferSchedule.objects.get(pk=instance.pk)
                    old_time = old.departure_time
                except TransferSchedule.DoesNotExist:
                    pass

            if not instance.departure_date:
                instance.departure_date = instance.group.date

            instance.save()

            if old_time and old_time != instance.departure_time:
                from_time = old_time.strftime('%H:%M')
                to_time = instance.departure_time.strftime('%H:%M')

                self.log_change(
                    request,
                    instance,
                    f"Время трансфера изменено: отель {instance.hotel.name}, дата {instance.group.date.strftime('%d.%m.%Y')}, с {from_time} на {to_time}"
                )

                TransferChangeLog.objects.create(
                    schedule=instance,
                    hotel_name=instance.hotel.name,
                    date=instance.group.date,
                    old_time=old_time,
                    new_time=instance.departure_time,
                    changed_by=request.user.username,
                    changed_at=now()
                )

                # === 🔁 Уведомления (твоя логика — без изменений)
                notifications = TransferNotification.objects.filter(
                    hotel=instance.hotel,
                    departure_date=instance.group.date,
                    transfer_type=instance.group.transfer_type,
                )

                print(f"\n[DEBUG] Сохранили трансфер: {instance.hotel.name}, {instance.group.date}, время {instance.departure_time}")
                print(f"[DEBUG] Фамилия пассажира в расписании: '{instance.passenger_last_name}'")

                for notif in notifications:
                    notif_last = (notif.last_name or "").strip().lower()
                    schedule_last = (instance.passenger_last_name or "").strip().lower()

                    print(f"[CHECK] Сравниваем '{notif_last}' == '{schedule_last}'")

                    if notif.transfer_type == 'private' and notif.last_name:
                        has_match = instance.passengers.filter(last_name__iexact=notif.last_name.strip()).exists()
                        if not has_match:
                            print(f"[SKIP] Фамилия не найдена среди пассажиров семьи — {notif.email}")
                            continue

                    else:
                        print(f"[GROUP] Это групповой трансфер или пустая фамилия — отправляем всем.")

                    # 🎯 В этот момент фамилия совпала — можно отправлять
                    activate(notif.language or 'ru')

                    subject = _("Transfer time has been updated")
                    lang_code = notif.language or 'en'
                    template_name = f"emails/transfer_time_changed_{lang_code}.html"

                    departure_time = instance.departure_time
                    pickup_point = instance.pickup_point

                    if not pickup_point:
                        pickup_point = PickupPoint.objects.filter(
                            hotel=notif.hotel,
                            transfer_type=notif.transfer_type
                        ).first()

                    pickup_name = pickup_point.name if pickup_point else None
                    map_link = (
                        f"https://www.google.com/maps?q={pickup_point.latitude},{pickup_point.longitude}"
                        if pickup_point and pickup_point.latitude and pickup_point.longitude
                        else None
                    )

                    try:
                        send_html_email(
                            subject=subject,
                            to_email=notif.email,
                            template_name=template_name,
                            context={
                                "hotel_name": notif.hotel.name,
                                "departure_date": notif.departure_date.strftime('%d.%m.%Y'),
                                "old_time": from_time,
                                "new_time": departure_time.strftime('%H:%M'),
                                "pickup_point": pickup_name,
                                "map_link": map_link,
                            }
                        )
                        notif.departure_time_sent = departure_time
                        notif.save(update_fields=["departure_time_sent"])
                        print(f"[OK] Уведомление отправлено на {notif.email}")

                    except Exception as e:
                        print(f"[ERROR] Не удалось отправить письмо {notif.email}: {e}")

        formset.save_m2m()
        deactivate_all()




@admin.register(TransferChangeLog)
class TransferChangeLogAdmin(admin.ModelAdmin):
    list_display = ('hotel_name', 'date', 'old_time', 'new_time', 'changed_by', 'changed_at')
    actions = ['export_to_excel']

    def export_to_excel(self, request, queryset):
        data = []
        for log in queryset:
            data.append({
                "Отель": log.hotel_name,
                "Дата": log.date.strftime('%d.%m.%Y'),
                "Старое время": log.old_time.strftime('%H:%M'),
                "Новое время": log.new_time.strftime('%H:%M'),
                "Кто изменил": log.changed_by,
                "Когда": log.changed_at.strftime('%d.%m.%Y %H:%M'),
            })

        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = f"Изменения_трансфера_{datetime.date.today()}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        df.to_excel(response, index=False)
        return response

    export_to_excel.short_description = "📥 Экспортировать в Excel"

# Админка для нотификаций по трансферам
@admin.register(TransferNotification)
class TransferNotificationAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'hotel', 'departure_date', 'transfer_type', 'language',
        'confirmation_token',  # 👈 ДОБАВЬ ЭТУ СТРОКУ
        'is_changed', 'is_confirmed_colored'
    )
    list_filter = ('transfer_type', 'departure_date', 'hotel', 'language', 
        'is_changed', 'is_confirmed'
    )

    search_fields = ('email',)

    def is_confirmed_colored(self, obj):
        color = 'green' if obj.is_confirmed else 'red'
        text = 'Да' if obj.is_confirmed else 'Нет'
        return format_html('<span style="color: {};">{}</span>', color, text)
    is_confirmed_colored.short_description = "Клиент подтвердил"


@admin.register(TransferInquiryLog)
class TransferInquiryLogAdmin(admin.ModelAdmin):
    list_display = ['inquiry', 'email', 'sent_at']
    search_fields = ['email', 'reply_content']
    list_filter = ['sent_at']

class TransferInquiryLogInline(admin.TabularInline):
    model = TransferInquiryLog
    extra = 0
    readonly_fields = ['email', 'reply_content', 'sent_at']
    can_delete = False

@admin.register(TransferInquiry)
class TransferInquiryAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'hotel', 'departure_date', 'email', 'created_at']
    list_filter = ['departure_date', 'hotel']
    search_fields = ['last_name', 'email', 'flight_number']
    readonly_fields = ['replied']
    actions = ['send_reply_email']

    def send_reply_email(self, request, queryset):
        for inquiry in queryset:
            if inquiry.reply and not inquiry.replied:
                self._send_email(inquiry)
        self.message_user(request, "Ответы успешно отправлены.")

    send_reply_email.short_description = "Отправить ответы туристам"

    def save_model(self, request, obj, form, change):
        if 'reply' in form.changed_data and obj.reply and not obj.replied:
            self._send_email(obj)
        super().save_model(request, obj, form, change)

    def _send_email(self, inquiry):
        subject = "Your transfer request"
        from_email = "CostaSolinfo.Malaga@gmail.com"
        to_email = [inquiry.email]

        context = {
            'name': inquiry.last_name,
            'reply': inquiry.reply,
            'hotel': inquiry.hotel.name if inquiry.hotel else '',
            'date': inquiry.departure_date,
            'flight': inquiry.flight_number,
        }

        # === ЯЗЫК ===
        supported_languages = ['ru', 'en', 'es', 'lv', 'lt', 'et', 'uk']
        lang = inquiry.language if inquiry.language in supported_languages else 'ru'
        template_path = f"emails/transfer_reply_{lang}.html"

        # === Рендер шаблона ===
        html_content = render_to_string(template_path, context)
        text_content = inquiry.reply

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

        # Обновить флаг
        inquiry.replied = True
        inquiry.save()

        # Лог
        TransferInquiryLog.objects.create(
            inquiry=inquiry,
            email=inquiry.email,
            reply_content=inquiry.reply
        )





# ------- Форма загрузки -------
class ExcursionPickupImportForm(forms.Form):
    excel_file = forms.FileField(label="Excel (pickup_points + excursion_times)")
    dry_run = forms.BooleanField(label="Только проверить (без сохранения)", required=False, initial=False)

# ------- Утилиты -------
def _norm(s):
    if s is None:
        return ""
    if isinstance(s, str):
        return s.strip()
    return str(s).strip()

def _parse_time(val):
    """Поддержка Excel-времени, строк '08:10'/'8:10'/'08:10:00', pandas Timestamp."""
    if val is None or (hasattr(val, "isna") and val.isna()):
        return None
    if isinstance(val, time):
        return val
    # pandas Timestamp или numpy datetime64
    if hasattr(val, "to_pydatetime"):
        return val.to_pydatetime().time()
    s = str(val).strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    # попытаемся из '8:5' привести к 08:05
    if ":" in s:
        hh, mm, *rest = s.split(":")
        if hh.isdigit() and mm.isdigit():
            try:
                return time(hour=int(hh), minute=int(mm))
            except Exception:
                return None
    return None

def _to_float(v):
    """Поддержка '36,637518', '36.637518', чисел и пустых значений."""
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    s = s.replace(',', '.')  # КЛЮЧЕВОЕ: заменяем запятую на точку
    try:
        return float(s)
    except Exception:
        return None

def _ensure_zones_exist(zone_names):
    """Создаёт в БД отсутствующие ExcursionZone по именам из Excel."""
    zone_names = {z for z in (zone_names or []) if z}
    if not zone_names:
        return 0
    existing = set(ExcursionZone.objects.filter(name__in=zone_names)
                   .values_list("name", flat=True))
    to_create = [ExcursionZone(name=z) for z in zone_names if z not in existing]
    if to_create:
        ExcursionZone.objects.bulk_create(to_create, batch_size=200)
    return len(to_create)

# ------- helpers --------------------------------------------------------------

def _haversine_km(lat1, lon1, lat2, lon2):
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except (TypeError, ValueError):
        return None
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))

def _choose_hotel_point(hotel, direction, points_here, default_point, snap_km_max: float = 1.0):
    """
    Правила (по приоритету):
      1) Если у отеля есть pickup_point И его имя есть в points_here -> берём его.
      2) Если в points_here есть точка с именем отеля -> берём её.
      3) Если есть координаты отеля и точек -> берём ближайшую.
         Если ближайшая дальше snap_km_max и в зоне >1 точки — возвращаем None (требуется ручная проверка).
      4) Если в зоне ровно 1 точка — берём её, иначе -> None.
    """
    zone_names_norm = {_norm(p.get("name")) for p in points_here if p.get("name")}
    points_by_name = {_norm(p.get("name")): p for p in points_here if p.get("name")}

    # 1) собственная точка у отеля, если она действительно есть в этой зоне/направлении
    hotel_pp = getattr(hotel, "pickup_point", None)
    if getattr(hotel_pp, "name", None):
        pp_norm = _norm(hotel_pp.name)
        if pp_norm in zone_names_norm:
            return {
                "name": hotel_pp.name,
                "latitude": getattr(hotel_pp, "latitude", None),
                "longitude": getattr(hotel_pp, "longitude", None),
            }

    # 2) совпадение по имени
    hotel_name_norm = _norm(getattr(hotel, "name", None))
    if hotel_name_norm and hotel_name_norm in points_by_name:
        return points_by_name[hotel_name_norm]

    # 3) ближайшая по координатам
    best = None
    best_d = None
    if hotel.latitude is not None and hotel.longitude is not None:
        for p in points_here:
            lat = p.get("latitude"); lng = p.get("longitude")
            if lat is None or lng is None:
                continue
            d = _haversine_km(hotel.latitude, hotel.longitude, lat, lng)
            if d is None:
                continue
            if best_d is None or d < best_d:
                best, best_d = p, d
    if best is not None:
        # если далеко от отеля — считаем назначение сомнительным
        if best_d is not None and best_d > snap_km_max and len(points_here) > 1:
            return None
        return best

    # 4) фолбэк: только если точка в зоне одна
    if len(points_here) == 1:
        return points_here[0]
    return None



# ------- Основной импортёр: разворот на все отели временной зоны --------------

def import_excursion_pickups_from_excel(file_obj, dry_run: bool = False):
    """
    Листы Excel:
      - pickup_points: pickup_point_name | zone | direction | latitude | longitude
      - excursion_times: excursion_name | zone | direction | pickup_time
      - [опц.] hotel_overrides: hotel | zone | direction | pickup_point_name
    """
    xl = pd.ExcelFile(file_obj)

    # === 1) Точки из справочника ===
    if "pickup_points" not in xl.sheet_names:
        raise ValueError("В файле нет листа 'pickup_points'.")
    df_points = pd.read_excel(xl, sheet_name="pickup_points")

    required_cols_points = {"pickup_point_name", "zone", "direction"}
    if not required_cols_points.issubset(set(df_points.columns)):
        raise ValueError(f"'pickup_points' должен содержать столбцы: {sorted(required_cols_points)}")

    df_points["pickup_point_name"] = df_points["pickup_point_name"].map(_norm)
    df_points["zone"] = df_points["zone"].map(_norm)
    df_points["direction"] = df_points["direction"].map(_norm)

    # широта/долгота — поддержка '36,6375'
    for col in ("latitude", "longitude"):
        if col in df_points.columns:
            df_points[col] = df_points[col].apply(_to_float)
        else:
            df_points[col] = None

    # соберём (direction, zone) -> список уникальных точек
    points_by_zone = {}
    upsert_points = []
    seen = set()  # чтобы не плодить дубли в списке зоны

    for _, row in df_points.iterrows():
        name = row["pickup_point_name"]
        if not name:
            continue
        direction = row["direction"] or None
        zone = row["zone"] or None
        lat = row.get("latitude")
        lng = row.get("longitude")

        # upsert справочника по имени
        ref = ExcursionPickupReference.objects.filter(name=name).first()
        created_ref = False
        if not ref:
            if dry_run:
                created_ref = True
            else:
                ref = ExcursionPickupReference.objects.create(
                    name=name,
                    latitude=None if pd.isna(lat) else lat,
                    longitude=None if pd.isna(lng) else lng,
                    default_time=None,
                )
                created_ref = True
        else:
            if not dry_run and (pd.notna(lat) or pd.notna(lng)):
                changed = False
                if pd.notna(lat) and ref.latitude != lat:
                    ref.latitude = lat; changed = True
                if pd.notna(lng) and ref.longitude != lng:
                    ref.longitude = lng; changed = True
                if changed:
                    ref.save(update_fields=["latitude", "longitude"])

        upsert_points.append((name, "created" if created_ref else "updated/kept"))

        key = (direction, zone)
        payload = {
            "name": name,
            "latitude": None if pd.isna(lat) else lat,
            "longitude": None if pd.isna(lng) else lng,
        }
        uniq_key = (key, name)
        if uniq_key not in seen:
            points_by_zone.setdefault(key, []).append(payload)
            seen.add(uniq_key)

    # === 1.5) Времена (и динамические зоны) ===
    if "excursion_times" not in xl.sheet_names:
        raise ValueError("В файле нет листа 'excursion_times'.")
    df_times = pd.read_excel(xl, sheet_name="excursion_times")

    required_cols_times = {"excursion_name", "zone", "direction", "pickup_time"}
    if not required_cols_times.issubset(set(df_times.columns)):
        raise ValueError(f"'excursion_times' должен содержать столбцы: {sorted(required_cols_times)}")

    df_times["excursion_name"] = df_times["excursion_name"].map(_norm)
    df_times["zone"] = df_times["zone"].map(_norm)
    df_times["direction"] = df_times["direction"].map(_norm)

    # создадим недостающие зоны по именам (если у вас есть ExcursionZone)
    zone_names = set(df_points["zone"].dropna().astype(str).str.strip()) | \
                 set(df_times["zone"].dropna().astype(str).str.strip())
    try:
        created_zones = 0 if dry_run else _ensure_zones_exist(zone_names)
    except Exception:
        created_zones = 0

    # --- необязательные оверрайды (лист hotel_overrides) ---
    hotel_override = {}
    if "hotel_overrides" in xl.sheet_names:
        df_ov = pd.read_excel(xl, sheet_name="hotel_overrides")
        need = {"hotel", "zone", "direction", "pickup_point_name"}
        if need.issubset(set(df_ov.columns)):
            for _, r in df_ov.fillna("").iterrows():
                h = _norm(r.get("hotel"))
                z = _norm(r.get("zone"))
                d = _norm(r.get("direction"))
                p = _norm(r.get("pickup_point_name"))
                if h and z and d and p:
                    hotel_override[(h, z, d)] = p

    # соответствия направлений Excel -> модель
    excel2model_dir = {"to_malaga": "GIB_TO_MALAGA", "to_gibraltar": "MALAGA_TO_GIB"}

    # === 2) Разворот на все отели выбранной временной зоны ===
    created_count = 0
    updated_count = 0
    skipped = []

    for _, row in df_times.iterrows():
        exc_name = row["excursion_name"]
        zone = row["zone"] or None
        excel_dir = row["direction"] or None
        tval = _parse_time(row["pickup_time"])

        if not exc_name:
            skipped.append((exc_name, excel_dir, zone, "empty excursion name")); continue
        exc = Excursion.objects.filter(title=exc_name).first()
        if not exc:
            skipped.append((exc_name, excel_dir, zone, "excursion not found")); continue

        model_dir = excel2model_dir.get(excel_dir)
        if model_dir and getattr(exc, "direction", None) and exc.direction != model_dir:
            skipped.append((exc_name, excel_dir, zone, "direction mismatch with excursion; used anyway"))

        key = (excel_dir, zone)
        points_here = points_by_zone.get(key) or []
        if not points_here:
            skipped.append((exc_name, excel_dir, zone, "no pickup points for this zone/direction")); continue

        if tval is None:
            skipped.append((exc_name, excel_dir, zone, "invalid time")); continue

        # все отели временной зоны
        try:
            hotels = Hotel.objects.filter(excursion_zone__name=zone)
        except Exception:
            skipped.append((exc_name, excel_dir, zone, "no hotel 'excursion_zone' field"))
            continue

        if not hotels.exists():
            skipped.append((exc_name, excel_dir, zone, "no hotels with this excursion zone")); continue

        default_point = points_here[0]

        for hotel in hotels:
            # 0) явный оверрайд из Excel?
            ov_name = hotel_override.get((_norm(hotel.name), zone, excel_dir))
            if ov_name:
                picked = next((p for p in points_here if _norm(p.get("name")) == ov_name), None)
                if not picked:
                    skipped.append((exc_name, excel_dir, zone,
                                    f"override for hotel '{hotel.name}' points to unknown '{ov_name}'"))
                    continue
            else:
                # выбираем корректную точку для отеля автоматически
                picked = _choose_hotel_point(hotel, model_dir or excel_dir, points_here, default_point)

            if not picked:
                skipped.append((exc_name, excel_dir, zone,
                                f"ambiguous for hotel '{hotel.name}': no exact/nearest match"))
                continue

            pp_name = picked["name"]
            ref_lat = picked.get("latitude")
            ref_lng = picked.get("longitude")

            if dry_run:
                created_count += 1
                continue

            # upsert по (excursion, hotel)
            obj, is_created = ExcursionPickupPoint.objects.get_or_create(
                excursion=exc,
                hotel=hotel,
                defaults={
                    "pickup_point_name": pp_name,
                    "pickup_time": tval,
                    "latitude": ref_lat,
                    "longitude": ref_lng,
                },
            )

            to_update = []
            if obj.pickup_point_name != pp_name:
                obj.pickup_point_name = pp_name; to_update.append("pickup_point_name")
            if obj.pickup_time != tval:
                obj.pickup_time = tval; to_update.append("pickup_time")
            if ref_lat is not None and getattr(obj, "latitude", None) != ref_lat:
                obj.latitude = ref_lat; to_update.append("latitude")
            if ref_lng is not None and getattr(obj, "longitude", None) != ref_lng:
                obj.longitude = ref_lng; to_update.append("longitude")

            if is_created:
                created_count += 1
            elif to_update:
                obj.save(update_fields=list(set(to_update)))
                updated_count += 1

    if not dry_run:
        # Удаляем «осиротевшие» записи (ранние итерации/ошибки)
        ExcursionPickupPoint.objects.filter(hotel__isnull=True).delete()

    return {
        "points_upserted": upsert_points,
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped,
        "created_zones": created_zones,
        "dry_run": dry_run,
    }


# ------- Вьюха для админки -------
def import_excursion_pickups_view(request):
    context = {"title": "Импорт точек и времени экскурсий"}
    if request.method == "POST":
        form = ExcursionPickupImportForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data["excel_file"]
            dry_run = form.cleaned_data["dry_run"]
            try:
                report = import_excursion_pickups_from_excel(f, dry_run=dry_run)
                # сообщения
                msg = f"Импорт завершён. Создано: {report['created']}, обновлено: {report['updated']}, пропущено: {len(report['skipped'])}. "
                if dry_run:
                    msg = "[DRY RUN] " + msg
                messages.success(request, msg)
                # подробности в шаблоне
                context["report"] = report
            except Exception as e:
                messages.error(request, f"Ошибка импорта: {e}")
    else:
        form = ExcursionPickupImportForm()
    context["form"] = form
    return render(request, "admin/core/excursions_import.html", context)




def download_excursion_template_view(request):
    # соберём актуальные данные из БД
    from .models import ExcursionPickupReference, Excursion
    points_qs = ExcursionPickupReference.objects.all().values(
        "name", "latitude", "longitude"
    )
    excursions_qs = Excursion.objects.all().values("title", "direction")

    # таблицы
    df_points = pd.DataFrame(list(points_qs))
    if not df_points.empty:
        df_points.rename(columns={
            "name": "pickup_point_name",
        }, inplace=True)
        df_points["zone"] = ""        # менеджер может заполнить руками
        df_points["direction"] = ""   # или оставить пустым
    else:
        df_points = pd.DataFrame(columns=["pickup_point_name","zone","direction","latitude","longitude"])

    df_times = pd.DataFrame(columns=["excursion_name","zone","direction","pickup_time"])
    for exc in excursions_qs:
        df_times.loc[len(df_times)] = [exc["title"], "", exc["direction"], ""]

    # пишем в память
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_points.to_excel(writer, sheet_name="pickup_points", index=False)
        df_times.to_excel(writer, sheet_name="excursion_times", index=False)
    output.seek(0)

    # отдаём файл
    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=excursions_template.xlsx'
    return response


def ensure_all_hotel_excursions(default_active=True):
    from .models import Hotel, Excursion, HotelExcursion
    existing = set(HotelExcursion.objects.values_list('hotel_id', 'excursion_id'))
    to_create = []
    for h_id in Hotel.objects.values_list('id', flat=True):
        for e_id in Excursion.objects.values_list('id', flat=True):
            if (h_id, e_id) not in existing:
                to_create.append(HotelExcursion(hotel_id=h_id, excursion_id=e_id, is_active=default_active))
    if to_create:
        HotelExcursion.objects.bulk_create(to_create, batch_size=2000)
    return len(to_create)
import pandas as pd
import datetime
from django.db import models
from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
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
    TransferPageContentBlock
)
from leaflet.admin import LeafletGeoAdmin
from leaflet.forms.widgets import LeafletWidget
from django import forms
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import now, localtime
from django.utils.translation import activate, deactivate_all, gettext as _
from core.utils import send_html_email, send_answer_notification
from .forms import ExcursionAdminForm, BulkTransferScheduleForm, ExcursionPickupPointForm

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
@admin.register(InfoMeeting)
class InfoMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date')

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


# Админка отели
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    fields = ('name', 'region', 'latitude', 'longitude')  # ❗ pickup_point убираем
    inlines = [PickupPointInline, InfoMeetingScheduleInline]  # 🆕 добавлен Inline
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


@admin.register(ExcursionPickupPoint)
class ExcursionPickupPointAdmin(admin.ModelAdmin):
    form = ExcursionPickupPointForm
    search_fields = ['pickup_point_name']
    list_display = ('id', 'get_hotel', 'get_excursion', 'pickup_time', 'get_region')
    fields = ('excursion', 'hotel', 'pickup_point_name', 'pickup_time', 'latitude', 'longitude', 'map_block')
    readonly_fields = ('map_block',)

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
    inlines = [ExcursionRegionPriceInline, ExcursionPickupInline, ExcursionImageInline]  # 👈 Добавили регионы

    fieldsets = (
        (None, {
            'fields': ('title', 'duration', 'direction', 'days', 'is_active')
        }),
        ('Фото и медиа', {
            'fields': ('image',)
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

class TransferScheduleItemInline(admin.TabularInline):
    model = TransferSchedule
    extra = 1  # сколько пустых строк по умолчанию,,,
    autocomplete_fields = ['hotel', 'pickup_point']
    fields = ('hotel', 'departure_time', 'pickup_point', 'passenger_last_name')
    show_change_link = True
    

@admin.register(TransferScheduleGroup)
class TransferScheduleGroupAdmin(admin.ModelAdmin):
    inlines = [TransferScheduleItemInline]

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

                # === 🔁 Уведомления
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
                        if notif_last != schedule_last:
                            print(f"[SKIP] Фамилия не совпала для {notif.email} — уведомление не отправляем.")
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






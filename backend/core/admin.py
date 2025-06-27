from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from .models import (
    Hotel, Excursion, PickupPoint,
    Homepage, InfoMeeting, AirportTransfer,
    Question, ContactInfo, AboutUs, TransferSchedule,
    Region, PageBanner, GroupTransferPickupPoint, PrivateTransferPickupPoint,
    TransferSchedule, TransferScheduleGroup, TransferNotification,
    TransferInquiry, TransferInquiryLog
)
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .forms import ExcursionAdminForm, BulkTransferScheduleForm

# Баннеры на старницах
@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    list_display = ('page', 'title_en')  # Показываем страницу и заголовок
    search_fields = ('page', 'title_en', 'title_ru')

# Главная страница
@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    list_display = ('title',)

# Инфо встреча
@admin.register(InfoMeeting)
class InfoMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date')

# Трансфер в аэропорт
@admin.register(AirportTransfer)
class AirportTransferAdmin(admin.ModelAdmin):
    list_display = ['id', 'departure_date', 'departure_time', 'contact_email']

# Задать вопрос
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('created_at',)

# Контакты
@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'email', 'phone', 'whatsapp')

#О нас
@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title',)

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
    inlines = [PickupPointInline]  # 🆕 добавлен Inline
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

# Админка экскурсии
@admin.register(Excursion)
class ExcursionAdmin(admin.ModelAdmin):
    form = ExcursionAdminForm  # ✅ это ОБЯЗАТЕЛЬНО
    list_display = ('title', 'direction', 'duration')
    list_filter = ('direction',)
    search_fields = ('title', 'description')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'duration', 'direction', 'days')
        }),
        ('Фото и медиа', {
            'fields': ('image',)
        }),
    )

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
                    if time_field:
                        pickup_point = PickupPoint.objects.filter(hotel=hotel, transfer_type=transfer_type).first()
                        TransferSchedule.objects.create(
                            transfer_type=transfer_type,
                            hotel=hotel,
                            departure_date=transfer_date,
                            departure_time=time_field,
                            pickup_point=pickup_point
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

# Массовое добавление даты и времени для трансферов
@admin.register(TransferSchedule)
class TransferScheduleAdmin(admin.ModelAdmin):
    list_display = ['transfer_type', 'hotel', 'departure_date', 'departure_time', 'pickup_point', 'passenger_last_name']
    list_filter = ['transfer_type', 'departure_date']
    search_fields = ['hotel__name', 'passenger_last_name']

    def save_formset(self, request, form, formset, change):
        """
        При сохранении каждого TransferSchedule внутри группы —
        автоматически подставляем дату и тип трансфера из родительской группы.
        """
        instances = formset.save(commit=False)
        for obj in instances:
            if form.instance:  # это объект TransferScheduleGroup
                obj.group = form.instance
                obj.departure_date = form.instance.date
                if not obj.transfer_type:
                    obj.transfer_type = form.instance.transfer_type
            obj.save()
        formset.save_m2m()

# Inline для TransferSchedule
class TransferScheduleInline(admin.TabularInline):
    model = TransferSchedule
    extra = 1  # сколько пустых строк по умолчанию
    autocomplete_fields = ['hotel', 'pickup_point']
    fields = ('hotel', 'departure_time', 'pickup_point', 'passenger_last_name')
    show_change_link = True

    

# Админка для TransferScheduleGroup  
@admin.register(TransferScheduleGroup)
class TransferScheduleGroupAdmin(admin.ModelAdmin):
    inlines = [TransferScheduleInline]
    list_display = ['date', 'transfer_type']

    def save_model(self, request, obj, form, change):
        # Сохраняем саму группу (TransferScheduleGroup)
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # Здесь formset — один из inlines (TransferScheduleInline)
        instances = formset.save(commit=False)
        for instance in instances:
            instance.group = form.instance  # Привязка к текущей группе
            instance.departure_date = form.instance.date  # Копируем дату из группы
            instance.transfer_type = form.instance.transfer_type  # Копируем тип трансфера
            instance.save()
        formset.save_m2m()

# Админка для нотификаций по трансферам
@admin.register(TransferNotification)
class TransferNotificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'hotel', 'departure_date', 'transfer_type', 'language')
    list_filter = ('transfer_type', 'departure_date', 'hotel', 'language')
    search_fields = ('email',)

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
        subject = "Ответ на ваш запрос по трансферу"
        from_email = "info@costasolinfo.com"
        to_email = [inquiry.email]

        context = {
            'name': inquiry.last_name,
            'reply': inquiry.reply,
            'hotel': inquiry.hotel.name if inquiry.hotel else '',
            'date': inquiry.departure_date,
            'flight': inquiry.flight_number,
        }

        html_content = render_to_string("emails/transfer_reply.html", context)
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


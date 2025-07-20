import pandas as pd
import datetime
from django.contrib import admin, messages
from django.core.mail import EmailMultiAlternatives, send_mail
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from .models import (
    Hotel, Excursion, PickupPoint,
    Homepage, InfoMeeting, AirportTransfer,
    Question, ContactInfo, AboutUs, TransferSchedule,
    Region, PageBanner, GroupTransferPickupPoint, PrivateTransferPickupPoint,
    TransferSchedule, TransferScheduleGroup, TransferNotification,
    TransferInquiry, TransferInquiryLog, TransferScheduleItem,
    TransferChangeLog, PrivacyPolicy, Homepage, InfoMeetingScheduleItem
)
from django import forms
from ckeditor.widgets import CKEditorWidget
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.timezone import now, localtime
from django.utils.translation import activate, deactivate_all, gettext as _
from core.utils import send_html_email
from .forms import ExcursionAdminForm, BulkTransferScheduleForm

# Баннеры на старницах
@admin.register(PageBanner)
class PageBannerAdmin(admin.ModelAdmin):
    list_display = ('page', 'title_en')  # Показываем страницу и заголовок
    search_fields = ('page', 'title_en', 'title_ru')

# Главная страница
class HomepageAdminForm(forms.ModelForm):
    class Meta:
        model = Homepage
        fields = '__all__'
        widgets = {
            'subtitle': CKEditorWidget(),  # пример
            'subtitle_ru': CKEditorWidget(),
            'subtitle_en': CKEditorWidget(),
            'subtitle_es': CKEditorWidget(),
            'subtitle_lv': CKEditorWidget(),
            'subtitle_lt': CKEditorWidget(),
            'subtitle_uk': CKEditorWidget(),
            'subtitle_et': CKEditorWidget(),
            # Добавь другие поля, которые хочешь сделать форматируемыми
        }

@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    form = HomepageAdminForm
    list_display = ('title',)



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

# # Массовое добавление даты и времени для трансферов
# @admin.register(TransferSchedule)
# class TransferScheduleAdmin(admin.ModelAdmin):
#     list_display = ['transfer_type', 'hotel', 'departure_date', 'departure_time', 'pickup_point', 'passenger_last_name']
#     list_filter = ['transfer_type', 'departure_date']
#     search_fields = ['hotel__name', 'passenger_last_name']

#     def save_formset(self, request, form, formset, change):
#         """
#         При сохранении каждого TransferSchedule внутри группы —
#         автоматически подставляем дату и тип трансфера из родительской группы.
#         """
#         instances = formset.save(commit=False)
#         for obj in instances:
#             if form.instance:  # это объект TransferScheduleGroup
#                 obj.group = form.instance
#                 obj.departure_date = form.instance.date
#                 if not obj.transfer_type:
#                     obj.transfer_type = form.instance.transfer_type
#             obj.save()
#         formset.save_m2m()

# @admin.register(TransferScheduleItem)
# class TransferScheduleItemAdmin(admin.ModelAdmin):
#     list_display = ('hotel', 'group', 'time', 'tourist_last_name')
#     list_filter = ('group', 'hotel')
#     search_fields = ('tourist_last_name',)

# # Inline для TransferSchedule
# class TransferScheduleInline(admin.TabularInline):
#     model = TransferSchedule
#     extra = 1  # сколько пустых строк по умолчанию
#     autocomplete_fields = ['hotel', 'pickup_point']
#     fields = ('hotel', 'departure_time', 'pickup_point', 'passenger_last_name')
#     show_change_link = True

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


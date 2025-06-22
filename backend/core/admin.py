from django.contrib import admin
from .models import (
    Hotel, Excursion, PickupPoint,
    Homepage, InfoMeeting, AirportTransfer,
    Question, ContactInfo, AboutUs, TransferSchedule,
    Region, PageBanner
)
from django.utils.safestring import mark_safe
from .forms import ExcursionAdminForm  # импортируем форму

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

# Детальный трансфер по отелям и категориям
@admin.register(TransferSchedule)
class TransferScheduleAdmin(admin.ModelAdmin):
    list_display = ['transfer_type', 'hotel', 'departure_date', 'departure_time', 'pickup_point', 'passenger_last_name']
    list_filter = ['transfer_type', 'departure_date']
    search_fields = ['hotel__name', 'passenger_last_name']

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

# Админка отели
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    search_fields = ['name']
    fields = ('name', 'region', 'latitude', 'longitude', 'pickup_point')
    readonly_fields = ()

    class Media:
        js = (
            "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js",
        )
        css = {
            "all": (
                "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css",
                "admin/css/admin_custom.css",  # наш CSS
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

# Привязка точек сбора к отелям на трансферах
class HotelInline(admin.TabularInline):
    model = Hotel
    extra = 0
    autocomplete_fields = ['pickup_point']
    fields = ('name', 'latitude', 'longitude')
    show_change_link = True


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

# Админка точек сбора
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    search_fields = ['name']
    exclude = ('region',)  # ❗️это уберёт поле из формы
    list_display = ('name', 'latitude', 'longitude')
    inlines = [HotelInline]
    autocomplete_fields = ['hotel']

    class Media:
        js = [
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/pickup_point_map.js',
        ]
        css = {
            'all': ['https://unpkg.com/leaflet@1.9.4/dist/leaflet.css']
        }

    list_display = ('name', 'latitude', 'longitude')

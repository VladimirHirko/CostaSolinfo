from django.contrib import admin
from .models import (
    Hotel, Excursion, PickupPoint,
    Homepage, InfoMeeting, AirportTransfer,
    Question, ContactInfo, AboutUs
)
from .forms import ExcursionAdminForm  # импортируем форму

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
    list_display = ('description', 'price', 'contact_email')

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
    list_display = ('name', 'region', 'pickup_point')
    list_filter = ('region',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'region', 'pickup_point')
        }),
    )

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
    list_display = ('name', 'region', 'latitude', 'longitude')
    list_filter = ('region',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'region')
        }),
        ('Координаты', {
            'fields': ('latitude', 'longitude')
        }),
    )

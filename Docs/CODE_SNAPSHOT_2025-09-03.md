# Code Snapshot — 2025-09-03

---
## backend/manage.py

```py
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'costasolinfo.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

---
## backend/core/apps.py

```py
# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # ленивое подключение, чтобы избежать круговых импортов
        from . import signals
        signals.connect_signals()

```

---
## backend/core/models.py

```py
import uuid
from django.db import models
from django.db.models import Q, UniqueConstraint

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ckeditor.fields import RichTextField
from django.contrib.gis.db import models as geomodels

import logging
logger = logging.getLogger(__name__)

TRANSFER_TYPE_CHOICES = [
        ('group', 'Групповой'),
        ('private', 'Индивидуальный'),
    ]


# Модель баннеров на сайте
class PageBanner(models.Model):
    PAGE_CHOICES = [
        ('home', 'Главная'),
        ('excursions', 'Экскурсии'),
        ('info_meeting', 'Инфо встреча'),
        ('airport_transfer', 'Трансфер в аэропорт'),
        ('ask', 'Задать вопрос'),
        ('contacts', 'Контакты'),
        ('about', 'О нас'),
        ('group_transfer', 'Групповой трансфер'),  # 🟢 ДОБАВЬ ЭТО
        ('private_transfer', 'Индивидуальный трансфер')
    ]

    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    image = models.ImageField(upload_to='uploads/banners/')
    title_ru = models.CharField(max_length=200, blank=True, null=True)
    title_en = models.CharField(max_length=200, blank=True, null=True)
    title_es = models.CharField(max_length=200, blank=True, null=True)
    title_uk = models.CharField(max_length=200, blank=True, null=True)
    title_et = models.CharField(max_length=200, blank=True, null=True)
    title_lv = models.CharField(max_length=200, blank=True, null=True)
    title_lt = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры страниц"  # это то, что будет отображаться в админке

    def __str__(self):
        return f"Баннер для: {self.page}"

# Главной страницы
class Homepage(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    subtitle = RichTextField(blank=True, default='', verbose_name="Подзаголовок")  # ← было TextField
    banner_image = models.ImageField(upload_to='uploads/homepage/', verbose_name="Баннер")

    def __str__(self):
        return "Главная страница"

    class Meta:
        verbose_name = "Главная"
        verbose_name_plural = "Главная"

# Инфо встреча
class InfoMeeting(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True)
    date = models.DateField(blank=True, null=True)  # Можно оставить для общей даты
    time = models.TimeField(blank=True, null=True)  # и времени, если нужно
    # Можно будет не использовать, если переходим на расписание

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Инфо встреча"
        verbose_name_plural = "Инфо встречи"


class InfoMeetingScheduleItem(models.Model):
    #meeting = models.ForeignKey(InfoMeeting, on_delete=models.CASCADE, related_name='schedules')
    hotel = models.ForeignKey('core.Hotel', on_delete=models.CASCADE)

    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()

    class Meta:
        verbose_name = "Расписание инфо встречи"
        verbose_name_plural = "Расписания инфо встреч"
        ordering = ['date', 'time_from', 'time_to', 'hotel']

    def __str__(self):
        return f"{self.hotel.name} — {self.date} ({self.time_from}–{self.time_to})"


# Трансфер в аэропорт 
class AirportTransfer(models.Model):
    description = models.TextField()
    pickup_location = models.CharField(max_length=255, blank=True)  # новое мультиязычное поле
    departure_date = models.DateField(blank=True, null=True)
    departure_time = models.TimeField(blank=True, null=True)        # поле времени
    contact_email = models.EmailField()

    def __str__(self):
        return f"Airport Transfer Info"

    class Meta:
        verbose_name = "Трансфер в аэропорт"
        verbose_name_plural = "Трансферы в аэропорт"

# --- Текстовые блоки для страниц трансферов ---
class TransferPageContentBlock(models.Model):
    PAGE_CHOICES = [
        ('transfer_home', 'Трансферы (общая страница)'),
        ('transfer_group', 'Групповой трансфер'),
        ('transfer_private', 'Индивидуальный трансфер'),
    ]

    page = models.CharField(max_length=32, choices=PAGE_CHOICES, db_index=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Показывать")

    # Заголовки
    title_ru = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [ru]")
    title_en = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [en]")
    title_es = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [es]")
    title_lt = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [lt]")
    title_lv = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [lv]")
    title_et = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [et]")
    title_uk = models.CharField(max_length=255, blank=True, default='', verbose_name="Заголовок [uk]")

    # HTML-контент
    content_ru = models.TextField(blank=True, default='', verbose_name="Содержание [ru]")
    content_en = models.TextField(blank=True, default='', verbose_name="Содержание [en]")
    content_es = models.TextField(blank=True, default='', verbose_name="Содержание [es]")
    content_lt = models.TextField(blank=True, default='', verbose_name="Содержание [lt]")
    content_lv = models.TextField(blank=True, default='', verbose_name="Содержание [lv]")
    content_et = models.TextField(blank=True, default='', verbose_name="Содержание [et]")
    content_uk = models.TextField(blank=True, default='', verbose_name="Содержание [uk]")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Блок контента (трансферы)"
        verbose_name_plural = "Блоки контента (трансферы)"
        ordering = ('page', 'order', 'id')

    def __str__(self):
        return f"{self.get_page_display()} — #{self.order} — {self.title_ru or self.title_en or 'без заголовка'}"



# Детальный трансфер по категориям и отелям
class TransferSchedule(models.Model):
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE_CHOICES,
        verbose_name="Тип трансфера"
    )
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, verbose_name="Отель")
    departure_date = models.DateField(verbose_name="Дата выезда")
    pickup_point = models.ForeignKey('PickupPoint', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Точка сбора")
    
    booking_service_number = models.CharField(
        max_length=50, blank=True, db_index=True, verbose_name="Номер услуги/заявки"
    )
    departure_time = models.TimeField("Время выезда", null=True, blank=True)  # чтобы импортировать без времени

    passenger_last_name = models.CharField(max_length=100, blank=True, verbose_name="Фамилия туриста (если нужно)")
    group = models.ForeignKey(
        'TransferScheduleGroup',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='schedules',
        verbose_name="Группа трансфера"
    )

    def save(self, *args, **kwargs):
        if self.hotel and not self.pickup_point:
            self.pickup_point = self.hotel.pickup_point
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transfer_type_display()} | {self.hotel.name} | {self.departure_date}"

    class Meta:
        verbose_name = "Расписание трансфера"
        verbose_name_plural = "Массовое добавление расписания трансферов"
        ordering = ['departure_date', 'departure_time']

# Создание группы трансферов для редактирования
class TransferScheduleGroup(models.Model):
    date = models.DateField(verbose_name="Дата трансфера")
    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE_CHOICES,
        verbose_name="Тип трансфера"
    )

    def __str__(self):
        return f"{self.get_transfer_type_display()} — {self.date}"

class TransferPassenger(models.Model):
    schedule = models.ForeignKey(
        'TransferSchedule', on_delete=models.CASCADE, related_name='passengers'
    )
    last_name = models.CharField(max_length=100, db_index=True, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, blank=True, verbose_name="Имя")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['schedule', 'last_name', 'first_name'],
                condition=~Q(first_name=''),
                name='uniq_passenger_when_first_name_present',
            )
        ]
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()


# Модель для подписки TransferNotification
class TransferNotification(models.Model):
    email = models.EmailField(verbose_name=_("Email"))
    transfer_type = models.CharField(
        max_length=10,
        choices=[('group', _("Group")), ('private', _("Private"))],
        verbose_name=_("Transfer Type")
    )
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, verbose_name=_("Hotel"))
    departure_date = models.DateField(verbose_name=_("Departure Date"))
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default='ru',
        verbose_name=_("Language")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    departure_time_sent = models.TimeField(
        null=True, blank=True,
        verbose_name=_("Sent Departure Time")
    )
    last_name = models.CharField(max_length=100, blank=True, null=True)

    is_changed = models.BooleanField(default=False, verbose_name="Трансфер изменен")
    is_confirmed = models.BooleanField(default=False, verbose_name="Клиент подтвердил получение")
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _("Transfer Notification")
        verbose_name_plural = _("Transfer Notifications")

    def __str__(self):
        return f"{self.email} ({self.hotel}) {self.departure_date} [{self.transfer_type}]"

# Модель логов изменения трансферов
class TransferChangeLog(models.Model):
    schedule = models.ForeignKey(TransferSchedule, on_delete=models.CASCADE)
    hotel_name = models.CharField(max_length=255)
    date = models.DateField()
    old_time = models.TimeField()
    new_time = models.TimeField()
    changed_by = models.CharField(max_length=150)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel_name} | {self.date} | {self.old_time} → {self.new_time}"
 



# Задать вопрос
class Question(models.Model):
    CATEGORY_CHOICES = [
        ('transfer', 'Вопрос по трансферу'),
        ('excursion', 'Вопрос по экскурсии'),
        ('organization', 'Организационный вопрос'),
        ('other', 'Другое'),
    ]

    LANG_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'English'),
        ('es', 'Español'),
        ('lt', 'Lietuvių'),
        ('lv', 'Latviešu'),
        ('et', 'Eesti'),
        ('uk', 'Українська'),
    ]

    SOURCE_CHOICES = [
        ('ask', 'Страница «Задать вопрос»'),
        ('contacts', 'Страница «Контакты»'),
    ]

    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    hotel = models.CharField(max_length=255, blank=True, null=True, verbose_name="Отель")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория", default="other")
    question = models.TextField(verbose_name="Текст вопроса", blank=False, null=False)
    language = models.CharField(max_length=5, choices=LANG_CHOICES, verbose_name="Язык", default="ru")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="Источник", default='ask')  # ✅ NEW
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    answer = models.TextField("Ответ", blank=True, null=True)

    def __str__(self):
        return f"{self.name} — {self.get_category_display()} ({self.get_language_display()})"

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        logger.debug("[Question.save] BEFORE id=%s question=%r", getattr(self, 'id', None), getattr(self, 'question', None))
        super().save(*args, **kwargs)
        logger.debug("[Question.save] AFTER  id=%s question=%r", getattr(self, 'id', None), getattr(self, 'question', None))


# Контакты
class ContactInfo(models.Model):
    office_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    whatsapp = models.CharField(max_length=50, blank=True)
    address = models.TextField()

    def __str__(self):
        return self.office_name

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

# О нас
class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='about/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "О нас"
        verbose_name_plural = "О нас"

# Регионы
class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название региона")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"

# Отели
class Hotel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название отеля")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота")
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True, blank=True, related_name='hotels')

    pickup_point = models.ForeignKey(
        'PickupPoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_hotel',  # 👈 добавлено
        verbose_name="Точка сбора"
    )

    # НОВОЕ: временная зона экскурсий
    excursion_zone = models.ForeignKey(
        'core.ExcursionZone', 
        on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hotels',
        verbose_name="Временная зона (экскурсии)"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']  # по имени
        verbose_name = "Отель"
        verbose_name_plural = "Отели"

class ExcursionZone(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name="Временная зона (экскурсии)")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Временная зона (экскурсии)"
        verbose_name_plural = "Временные зоны (экскурсии)"

    def __str__(self):
        return self.name


class TransferScheduleItem(models.Model):
    group = models.ForeignKey('TransferScheduleGroup', on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    time = models.TimeField()
    pickup_point = models.CharField(max_length=255, blank=True)
    tourist_last_name = models.CharField(max_length=100, blank=True)

# Модель формы обратной связи если фамилия не найдена на индивидуальном трансфере
class TransferInquiry(models.Model):
    last_name = models.CharField(max_length=100)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True)
    departure_date = models.DateField()
    flight_number = models.CharField(max_length=50, blank=True)
    message = models.TextField(blank=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=10, default='ru')

    # Новое поле:
    reply = models.TextField(blank=True, verbose_name="Ответ админа")

    # метка — было ли письмо отправлено
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.last_name} — {self.departure_date}"

# Модель сохранения логов отправки песием по трансферам.
class TransferInquiryLog(models.Model):
    inquiry = models.ForeignKey(TransferInquiry, on_delete=models.CASCADE, related_name='logs')
    email = models.EmailField()
    reply_content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.email} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"



# Модель точки сбора 
class PickupPoint(models.Model):
    TRANSFER_TYPE_CHOICES = [
        ('group', 'Групповой трансфер'),
        ('private', 'Индивидуальный трансфер'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название точки сбора")
    location_description = models.TextField(blank=True, null=True, verbose_name="Описание/примечание")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    region = models.CharField(max_length=100, verbose_name="Регион")

    hotel = models.ForeignKey(  # 🟢 РАЗРЕШАЕТ МНОГО ТОЧЕК НА 1 ОТЕЛЬ
        'Hotel',
        on_delete=models.CASCADE,
        verbose_name="Отель",
        related_name='pickup_points',  # 🔁 теперь related_name — список, а не один объект
        null=True,
        blank=True
    )

    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE_CHOICES,
        default='group',
        verbose_name="Тип трансфера"
    )

    def __str__(self):
        return f"{self.name} ({self.get_transfer_type_display()})"

    class Meta:
        verbose_name = "Точки сбора для трансферов"
        verbose_name_plural = "Точки сбора для трансферов"

# Модель группового трансфера
class GroupTransferPickupPoint(PickupPoint):
    class Meta:
        proxy = True
        verbose_name = "Точка сбора (Групповой трансфер)"
        verbose_name_plural = "Точки сбора для группового трансфера"

# Модель индивидуального трансфера
class PrivateTransferPickupPoint(PickupPoint):
    class Meta:
        proxy = True
        verbose_name = "Точка сбора (Индивидуальный трансфер)"
        verbose_name_plural = "Точки сбора для индивидуального трансфера"


class HotelExcursion(models.Model):
    hotel = models.ForeignKey(
        'core.Hotel',                 # ← строковая ссылка
        on_delete=models.CASCADE,
        related_name='excursion_flags',
        verbose_name='Отель',
    )
    excursion = models.ForeignKey(
        'core.Excursion',             # ← строковая ссылка
        on_delete=models.CASCADE,
        related_name='hotel_flags',
        verbose_name='Экскурсия',
    )
    is_active = models.BooleanField(default=True, verbose_name='Доступна из отеля')

    class Meta:
        unique_together = ('hotel', 'excursion')
        verbose_name = 'Доступность экскурсии из отеля'
        verbose_name_plural = 'Доступность экскурсий из отеля'

    def __str__(self):
        return f'{self.hotel} ↔ {self.excursion} ({ "ON" if self.is_active else "OFF"})'



# Экскурсии
class Excursion(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Понедельник'),
        ('tue', 'Вторник'),
        ('wed', 'Среда'),
        ('thu', 'Четверг'),
        ('fri', 'Пятница'),
        ('sat', 'Суббота'),
        ('sun', 'Воскресенье'),
    ]

    DIRECTION_CHOICES = [
        ('MALAGA_TO_GIB', 'От Малаги к Гибралтару'),
        ('GIB_TO_MALAGA', 'От Гибралтара к Малаге'),
    ]
    direction = models.CharField(
        max_length=20,
        choices=DIRECTION_CHOICES,
        default='MALAGA_TO_GIB',
        verbose_name="Направление маршрута"
    )

    title = models.CharField(max_length=200, verbose_name="Название")
    
    duration = models.PositiveIntegerField(verbose_name="Продолжительность (часы)")
    image = models.ImageField(upload_to='excursions/', blank=True, null=True, verbose_name="Главное изображение")
    days = models.JSONField(verbose_name="Дни недели", help_text="Список дней: mon, tue и т.д.")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"

class ExcursionImage(models.Model):
    excursion = models.ForeignKey(
        "Excursion",
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="excursions/gallery/")
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.alt_text or f"Фото {self.id}"

class ExcursionRegionPrice(models.Model):
    excursion = models.ForeignKey(
        Excursion,
        on_delete=models.CASCADE,
        related_name="region_prices",
        verbose_name="Экскурсия"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        verbose_name="Регион"
    )
    price_adult = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена взрослый")
    price_child = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена ребёнок")

    class Meta:
        unique_together = ('excursion', 'region')
        verbose_name = "Цена экскурсии по региону"
        verbose_name_plural = "Цены экскурсий по регионам"

    def __str__(self):
        return f"{self.excursion.title} - {self.region.name}"


class ExcursionPickupPoint(models.Model):
    excursion = models.ForeignKey(
        'core.Excursion',
        on_delete=models.CASCADE,
        related_name='pickup_points',
        verbose_name='Экскурсия',
    )

    # может быть null на переходный период; уникальность ниже учитывает это условием
    hotel = models.ForeignKey(
        'core.Hotel',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='excursion_pickups',
        verbose_name='Отель',
    )

    # — вспомогательные ссылки для автозаполнения полей точки —
    copy_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clones',
        verbose_name='Использовать готовую точку',
    )

    pickup_reference = models.ForeignKey(
        'core.ExcursionPickupReference',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excursion_pickups',
        verbose_name='Справочник точки',
    )

    pickup_point = models.ForeignKey(
        'core.PickupPoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excursion_pickups',
        verbose_name='Точка сбора',
    )

    pickup_point_name = models.CharField(
        max_length=200,
        verbose_name="Название точки сбора",
        blank=True,
    )
    pickup_time = models.TimeField(
        verbose_name="Время отправления",
        null=True,
        blank=True,
    )

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True, verbose_name="Широта",
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True, verbose_name="Долгота",
    )

    def save(self, *args, **kwargs):
        """
        Приоритет автозаполнения:
        1) copy_from      → копируем name/lat/lng (+время, если у нас его нет)
        2) pickup_reference → берём name/lat/lng (+default_time, если времени нет)
        3) pickup_point   → если name/coords не заданы, подставляем из FK
        """
        if self.copy_from_id:
            src = self.copy_from
            if src:
                self.pickup_point_name = src.pickup_point_name
                self.latitude = src.latitude
                self.longitude = src.longitude
                if not self.pickup_time:
                    self.pickup_time = src.pickup_time

        elif self.pickup_reference_id:
            ref = self.pickup_reference
            if ref:
                self.pickup_point_name = ref.name
                self.latitude = ref.latitude
                self.longitude = ref.longitude
                if not self.pickup_time and getattr(ref, "default_time", None):
                    self.pickup_time = ref.default_time

        elif self.pickup_point_id:
            pp = self.pickup_point
            if pp:
                if not self.pickup_point_name:
                    self.pickup_point_name = getattr(pp, "name", "") or self.pickup_point_name
                if self.latitude is None:
                    self.latitude = getattr(pp, "latitude", None)
                if self.longitude is None:
                    self.longitude = getattr(pp, "longitude", None)

        super().save(*args, **kwargs)

    @property
    def direction(self):
        return getattr(self.excursion, "direction", None)

    @property
    def price_adult(self):
        hotel = getattr(self, "hotel", None)
        if not hotel or not hotel.region:
            return None
        price = self.excursion.region_prices.filter(region=hotel.region).first()
        return getattr(price, "price_adult", None)

    @property
    def price_child(self):
        hotel = getattr(self, "hotel", None)
        if not hotel or not hotel.region:
            return None
        price = self.excursion.region_prices.filter(region=hotel.region).first()
        return getattr(price, "price_child", None)

    class Meta:
        verbose_name = "Точка сбора экскурсии"
        verbose_name_plural = "Точки сбора экскурсий"
        ordering = ["pickup_time", "hotel__name", "pickup_point_name"]  # ← добавили
        unique_together = ('excursion', 'hotel')
        constraints = [
            # уникальность только когда hotel не NULL — позволит хранить временные «осиротевшие» записи
            models.UniqueConstraint(
                fields=['excursion', 'hotel'],
                name='uniq_excursion_hotel',
                condition=Q(hotel__isnull=False),
            ),
        ]
        indexes = [
            models.Index(fields=['excursion', 'pickup_point_name'], name='idx_excursion_pickupname'),
        ]

    def __str__(self):
        hotel_name = self.hotel.name if self.hotel_id else 'Без отеля'
        return f"{self.pickup_point_name or '—'} ({hotel_name})"

# core/models.py
class ExcursionPickupReference(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название точки сбора")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    default_time = models.TimeField(null=True, blank=True, verbose_name="Время по умолчанию")

    class Meta:
        verbose_name = "Справочник точек сбора"
        verbose_name_plural = "Справочник точек сбора"

    def __str__(self):
        return self.name



class ExcursionContentBlock(models.Model):
    BLOCK_TYPES = [
        ('description', 'Описание'),
        ('rules', 'Правила проведения'),
        ('what_to_bring', 'Что иметь при себе'),
        ('custom', 'Дополнительно'),
    ]

    excursion = models.ForeignKey(
        'Excursion',
        on_delete=models.CASCADE,
        related_name='content_blocks',
        verbose_name="Экскурсия"
    )
    block_type = models.CharField(max_length=50, choices=BLOCK_TYPES, default='custom', verbose_name="Тип блока")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Заголовок")
    content = RichTextField(blank=True, null=True, verbose_name="Содержание")


    def __str__(self):
        return f"{self.excursion.title} — {self.get_block_type_display()}"

    class Meta:
        verbose_name = "Блок контента экскурсии"
        verbose_name_plural = "Блоки контента экскурсий"
        ordering = ['order']







# Модель политики конфиденциальности
from django.db import models

class PrivacyPolicy(models.Model):
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('en', 'English'),
        ('es', 'Español'),
        ('lt', 'Lietuvių'),
        ('lv', 'Latviešu'),
        ('et', 'Eesti'),
        ('uk', 'Українська'),
    ]

    language_code = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, unique=True)
    content = RichTextField(verbose_name='Текст политики')

    def __str__(self):
        return f"Политика конфиденциальности ({self.get_language_code_display()})"


class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    position = models.CharField(max_length=100, verbose_name="Должность")
    photo = models.ImageField(upload_to='team/', verbose_name="Фото")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        ordering = ['order']
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.name


```

---
## backend/core/admin.py

```py
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
    TransferPageContentBlock, TransferPassenger, HotelExcursion, ExcursionZone
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
    inlines = [ExcursionRegionPriceInline, ExcursionPickupInline, ExcursionImageInline, ExcursionHotelInline]  # 👈 Добавили регионы

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



```

---
## backend/core/forms.py

```py
from django import forms
from .models import Excursion, Hotel, TransferSchedule, PickupPoint, ExcursionPickupPoint
from datetime import date

# Форма для указания дней недели на экскурсии
class ExcursionAdminForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        ('mon', 'Понедельник'),
        ('tue', 'Вторник'),
        ('wed', 'Среда'),
        ('thu', 'Четверг'),
        ('fri', 'Пятница'),
        ('sat', 'Суббота'),
        ('sun', 'Воскресенье'),
    ]

    days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        label="Дни недели",
        required=True
    )

    class Meta:
        model = Excursion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.days:
            self.initial['days'] = self.instance.days

    def clean_days(self):
        return self.cleaned_data['days']  # сохранится как список

# Форма для указания времени на трансферы
class BulkTransferScheduleForm(forms.Form):
    transfer_type = forms.ChoiceField(choices=[('group', 'Групповой'), ('private', 'Индивидуальный')])
    transfer_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hotels = Hotel.objects.all()
        for hotel in hotels:
            self.fields[f'use_{hotel.id}'] = forms.BooleanField(label=hotel.name, required=False)
            self.fields[f'time_{hotel.id}'] = forms.TimeField(
                label='Время',
                required=False,
                widget=forms.TimeInput(attrs={'type': 'time'})
            )

class ExcursionPickupPointForm(forms.ModelForm):
    class Meta:
        model = ExcursionPickupPoint
        fields = '__all__'

    class Media:
        js = (
            'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
            'admin/js/leaflet_admin_pickup.js',
        )
        css = {
            'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)
        }
```

---
## backend/core/utils.py

```py
from rest_framework import serializers
from modeltranslation.utils import get_translation_fields
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

from django.conf import settings
from django.urls import reverse
from .models import TransferNotification
# from .email_utils import send_html_email  # или откуда у тебя вызывается send_html_email

# ⬇️ Для перевода тем писем
from django.utils.translation import gettext as _


class BaseTranslationSerializer(serializers.ModelSerializer):
    """
    Универсальный сериализатор, автоматически добавляющий переводы.
    Убираем мусорные поля вроде '_', 'a', 'l'.
    """
    translatable_fields = []
    extra_fields = []

    class Meta:
        model = None
        fields = []

    def __new__(cls, *args, **kwargs):
        # Все реальные поля модели
        valid_fields = {f.name for f in cls.Meta.model._meta.get_fields()} if cls.Meta.model else set()

        translated_fields = []
        if cls.Meta.model and hasattr(cls, 'translatable_fields'):
            for field in cls.translatable_fields:
                candidates = get_translation_fields(field)
                filtered = [f for f in candidates if f in valid_fields]
                translated_fields.extend(filtered)

        meta_extra = getattr(cls.Meta, 'extra_fields', [])
        extra_fields_clean = [f for f in meta_extra if f in valid_fields]

        # Итог: только валидные поля
        cls.Meta.fields = list(set(translated_fields + extra_fields_clean))

        print(f"[DEBUG CLEAN] Итоговые поля сериализатора: {cls.Meta.fields}")

        return super().__new__(cls)




# 🔹 Темы писем по шаблону и языку
def get_email_subject(template_name, lang):
    subjects = {
        'transfer_notification': {
            'ru': 'Информация о вашем трансфере',
            'en': 'Transfer Information',
            'es': 'Información sobre su traslado',
            'lv': 'Informācija par jūsu transfēru',
            'lt': 'Informacija apie jūsų pervežimą',
            'et': 'Teave teie transfeeri kohta',
            'uk': 'Інформація про ваш трансфер',
        },
        # Здесь можно добавить другие типы писем
    }

    key = template_name.replace('emails/', '').replace('.html', '').replace(f'_{lang}', '')
    return subjects.get(key, {}).get(lang, subjects.get(key, {}).get('en', 'CostaSolinfo Notification'))


# 🔹 Отправка HTML-письма
def send_html_email(subject, to_email, template_name, context, lang='en'):
    subject = get_email_subject(template_name, lang)
    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Это HTML письмо. Включите отображение HTML в вашем клиенте.",
        from_email="CostaSolinfo.Malaga@gmail.com",
        to=[to_email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_transfer_update_email(notification: TransferNotification):
    path = reverse('transfer_confirm', kwargs={"token": notification.confirmation_token})
    confirmation_link = f"{settings.SITE_URL}/api/transfer-confirm/{notification.confirmation_token}/"

    print("[DEBUG] Ссылка подтверждения:", confirmation_link)

    context = {
        'hotel_name': notification.hotel.name,
        'departure_date': notification.departure_date.strftime("%d.%m.%Y"),
        'new_time': notification.departure_time.strftime("%H:%M"),
        'pickup_point': notification.pickup_point.name if notification.pickup_point else None,
        'map_link': notification.map_link,
        'confirmation_link': confirmation_link,
    }

    send_html_email(
        subject="Время трансфера изменено",
        template="emails/transfer_notification_ru.html",
        context=context,
        to=[notification.email]
    )


def send_question_notification(question, lang_code=None):
    subject = f"Новый вопрос от {question.name}"
    recipient = getattr(settings, "QUESTION_NOTIFICATION_EMAIL", "costasolinfo.malaga@gmail.com")

    # если язык не передали — берём из модели
    if not lang_code:
        lang_code = getattr(question, "language", "ru")

    # вытаскиваем текст именно из нужного переводного поля
    question_text = getattr(question, f"question_{lang_code}", None) or question.question

    # Подготовим текст и HTML версии
    context = {"question": question, "lang_code": lang_code, "question_text": question_text}
    message_text = (
        f"Имя: {question.name}\n"
        f"Email: {question.email}\n"
        f"Отель: {question.hotel or '-'}\n"
        f"Категория: {question.get_category_display()}\n"
        f"Язык обращения: {lang_code}\n\n"
        f"Вопрос:\n{question_text}"
    )
    message_html = render_to_string("emails/question_notification.html", context)

    msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, [recipient])
    msg.attach_alternative(message_html, "text/html")
    msg.send()


def send_answer_notification(question):
    if not question.answer:
        return

    lang_code = getattr(question, "language", "ru")
    subject = {
        'ru': 'Ответ на ваш вопрос',
        'en': 'Answer to your question',
        'es': 'Respuesta a su pregunta',
        'lt': 'Atsakymas į jūsų klausimą',
        'lv': 'Atbilde uz jūsu jautājumu',
        'et': 'Vastus teie küsimusele',
        'uk': 'Відповідь на ваше запитання',
    }.get(lang_code, 'Ответ на ваш вопрос')

    context = {
        "question": question,
        "lang_code": lang_code,
    }

    text_body = render_to_string("emails/answer_notification.txt", context)
    html_body = render_to_string("emails/answer_notification.html", context)

    msg = EmailMultiAlternatives(
        subject,
        text_body,
        settings.DEFAULT_FROM_EMAIL,
        [question.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
```

---
## backend/core/signals.py

```py
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import activate, gettext as _
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import (
    TransferNotification, TransferSchedule, TransferScheduleItem, 
    TransferInquiry, TransferScheduleGroup, Hotel
)
#from .emails import send_transfer_change_email





@receiver(post_save, sender=TransferScheduleGroup)
def notify_transfer_group_updated(sender, instance, **kwargs):
    transfer_type = instance.transfer_type
    group_date = instance.date

    print("===============================================")
    print(f"[DEBUG] Группа трансфера сохранена: {group_date} ({transfer_type})")
    print("===============================================")

    # Получаем все связанные TransferScheduleItem
    items = TransferScheduleItem.objects.filter(group=instance)

    for item in items:
        hotel = item.hotel
        new_time = item.time
        last_name = (item.tourist_last_name or "").strip().lower()

        print(f"\n[ITEM] Отель: {hotel}, Время: {new_time}, Фамилия: {last_name}")

        if transfer_type == 'group':
            print("[INFO] Это групповой трансфер.")
            notifications = TransferNotification.objects.filter(
                hotel=hotel,
                departure_date=group_date,
                transfer_type='group'
            )
            print(f"[DEBUG] Найдено групповых подписчиков: {notifications.count()}")

        elif transfer_type == 'private':
            print("[INFO] Это индивидуальный трансфер.")

            if not last_name:
                print("[WARN] Не указана фамилия туриста — пропускаем.")
                continue

            all_notifications = TransferNotification.objects.filter(
                hotel=hotel,
                departure_date=group_date,
                transfer_type='private'
            )

            print(f"[DEBUG] Целевая фамилия для сравнения: '{last_name}'")
            print(f"[DEBUG] Всего найдено подписчиков: {all_notifications.count()}")

            notifications = []
            for notif in all_notifications:
                notif_lastname = (notif.last_name or "").strip().lower()
                print(f"[CHECK] Сравнение: '{notif_lastname}' == '{last_name}'")

                if notif_lastname == last_name:
                    print(f"[MATCH] Совпадение найдено: {notif.email}")
                    notifications.append(notif)

            print(f"[RESULT] Найдено совпадений по фамилии: {len(notifications)}")

        else:
            print("[WARN] Неизвестный тип трансфера — пропускаем item.")
            continue

        # Отправка писем
        for notif in notifications:
            if notif.departure_time_sent == new_time:
                print(f"[INFO] Уже отправлено время {new_time} для {notif.email} — пропускаем")
                continue

            activate(notif.language)

            subject = _("Изменение времени трансфера")
            message = _(
                f"Уважаемый(ая),\n\n"
                f"Время вашего трансфера из отеля {hotel.name} "
                f"на {group_date.strftime('%d.%m.%Y')} было изменено.\n"
                f"Новое время выезда: {new_time.strftime('%H:%M')}.\n\n"
                f"С уважением,\nКоманда CostaSolinfo"
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notif.email],
                    fail_silently=False
                )
                print(f"[OK] Письмо отправлено на {notif.email}")
            except Exception as e:
                print(f"[ERROR] Ошибка при отправке письма {notif.email}: {e}")
                continue

            notif.departure_time_sent = new_time
            notif.save(update_fields=["departure_time_sent"])
            print(f"[OK] Обновлено departure_time_sent для {notif.email}")



def autowire_hotel_excursions(sender, instance, created, **kwargs):
    """
    После сохранения отеля: если выставлена excursion_zone,
    создаём/обновляем строки ExcursionPickupPoint для всех Excursion,
    беря эталонное время/точку из первого найденного отеля той же зоны.
    Если в зоне ещё нет расписания – просто выходим (оно подтянется после импорта).
    """
    # если нет временной зоны — ничего не делаем
    if not getattr(instance, "excursion_zone_id", None):
        return

    # ЛЕНИВО получаем модели, чтобы не ловить NameError
    Excursion = apps.get_model("core", "Excursion")
    ExcursionPickupPoint = apps.get_model("core", "ExcursionPickupPoint")
    # Hotel = apps.get_model("core", "Hotel")  # не требуется прямо здесь

    with transaction.atomic():
        for exc in Excursion.objects.all().only("id"):
            # Эталон по зоне: любая запись этой экскурсии у отеля с той же зоной
            sample = (
                ExcursionPickupPoint.objects
                .filter(excursion=exc, hotel__excursion_zone_id=instance.excursion_zone_id)
                .values("pickup_time", "pickup_point_name", "latitude", "longitude")
                .first()
            )
            if not sample:
                # в зоне пока нет времени/точки — подтянется после импорта Excel
                continue

            # Точка отеля имеет приоритет, если задана
            pp_name = sample["pickup_point_name"]
            lat = sample["latitude"]
            lng = sample["longitude"]

            hotel_pp = getattr(instance, "pickup_point", None)
            if getattr(hotel_pp, "name", None):
                pp_name = hotel_pp.name
                lat = getattr(hotel_pp, "latitude", lat)
                lng = getattr(hotel_pp, "longitude", lng)

            obj, created_epp = ExcursionPickupPoint.objects.get_or_create(
                excursion=exc,
                hotel=instance,
                defaults={
                    "pickup_time": sample["pickup_time"],
                    "pickup_point_name": pp_name,
                    "latitude": lat,
                    "longitude": lng,
                },
            )

            if not created_epp:
                updates = {}
                if obj.pickup_time != sample["pickup_time"]:
                    updates["pickup_time"] = sample["pickup_time"]
                if obj.pickup_point_name != pp_name and pp_name:
                    updates["pickup_point_name"] = pp_name
                if lat is not None and obj.latitude != lat:
                    updates["latitude"] = lat
                if lng is not None and obj.longitude != lng:
                    updates["longitude"] = lng

                if updates:
                    for k, v in updates.items():
                        setattr(obj, k, v)
                    obj.save(update_fields=list(updates.keys()))


def connect_signals():
    """
    Подключаем сигнал лениво, чтобы не импортировать модели в модуле.
    """
    Hotel = apps.get_model("core", "Hotel")
    post_save.connect(
        autowire_hotel_excursions,
        sender=Hotel,
        dispatch_uid="core.autowire_hotel_excursions",
    )
```

---
## backend/core/views.py

```py
import Levenshtein

from datetime import datetime
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.throttling import AnonRateThrottle
from django.http import JsonResponse
from core.models import (
    Homepage, InfoMeeting, AirportTransfer, Question, 
    ContactInfo, AboutUs, Excursion, TransferSchedule, Hotel,
    PageBanner, Hotel, PickupPoint, TransferNotification,
    TransferInquiry, TransferScheduleItem, TransferScheduleGroup,
    PrivacyPolicy, InfoMeetingScheduleItem, ExcursionRegionPrice,
    PageBanner, ExcursionPickupPoint, Question, TeamMember, TransferPageContentBlock
    )
from core.utils import send_html_email, send_question_notification
from .serializers import (
    HomepageSerializer, InfoMeetingSerializer, AirportTransferSerializer,
    QuestionSerializer, ContactInfoSerializer, AboutUsSerializer, ExcursionSerializer,
    TransferScheduleRequestSerializer, TransferScheduleResponseSerializer,
    HotelSerializer, SimpleHotelSerializer, TransferNotificationCreateSerializer,
    TransferInquirySerializer, PrivacyPolicySerializer, InfoMeetingScheduleItemSerializer,
    PageBannerSerializer, ExcursionDetailSerializer, QuestionSerializer, TeamMemberSerializer,
    TransferPageContentBlockSerializer
    )
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib import admin
from django.conf import settings

from django.urls import path
from django.utils.translation import activate, get_language, gettext as _
from django.shortcuts import render, redirect
from .forms import BulkTransferScheduleForm
from .models import Hotel, TransferSchedule

from django.template.loader import render_to_string


from rest_framework.decorators import api_view
from rest_framework.response import Response
from Levenshtein import distance as levenshtein_distance
from .models import TransferScheduleGroup, TransferSchedule, PickupPoint, Hotel
from .throttling import ContactFormThrottle  # если у тебя оттуда
from .utils import send_question_notification
import logging

logger = logging.getLogger(__name__)

# Главное правило: RetrieveAPIView + queryset + serializer_class

import unicodedata

def normalize_last_name(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # убрать диакритику: Müller -> Muller
    return s.strip().casefold()  # регистр/пробелы


# Получение баннеров на страницах
def page_banner_api(request, page):
    try:
        banner = PageBanner.objects.get(page=page)
        data = {
            "image": banner.image.url if banner.image else "",
            "titles": {
                "ru": banner.title_ru,
                "en": banner.title_en,
                "es": banner.title_es,
                "uk": banner.title_uk,
                "et": banner.title_et,
                "lv": banner.title_lv,
                "lt": banner.title_lt,
            }
        }
        return JsonResponse(data)
    except PageBanner.DoesNotExist:
        return JsonResponse({"error": "Banner not found"}, status=404)

class PageBannerView(RetrieveAPIView):
    serializer_class = PageBannerSerializer
    lookup_field = "page"

    def get_object(self):
        page = self.kwargs.get("page")
        return PageBanner.objects.filter(page=page).first()

class HomepageView(RetrieveAPIView):
    queryset = Homepage.objects.all()
    serializer_class = HomepageSerializer

    def get_object(self):
        return self.queryset.first()

class InfoMeetingView(RetrieveAPIView):
    queryset = InfoMeeting.objects.all()
    serializer_class = InfoMeetingSerializer

    def get_object(self):
        return self.queryset.first()

from django.utils.timezone import now

@api_view(['GET'])
def info_meeting_schedule(request):
    hotel_id = request.query_params.get('hotel_id')
    if not hotel_id:
        return Response({"error": "hotel_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({"error": "Hotel not found"}, status=status.HTTP_404_NOT_FOUND)

    today = now().date()  # сегодняшняя дата

    schedule_items = InfoMeetingScheduleItem.objects.filter(
        hotel=hotel,
        date__gte=today  # 🔹 только даты сегодня и позже
    ).order_by('date', 'time_from')

    serializer = InfoMeetingScheduleItemSerializer(schedule_items, many=True)

    return Response({
        "hotel": hotel.name,
        "schedule": serializer.data
    })



# Трансферы
class AirportTransferView(RetrieveAPIView):
    queryset = AirportTransfer.objects.all()
    serializer_class = AirportTransferSerializer

    def get_object(self):
        return self.queryset.first()

class TransferContentListAPIView(generics.ListAPIView):
    serializer_class = TransferPageContentBlockSerializer

    def get_queryset(self):
        page = self.kwargs.get('page')
        return (TransferPageContentBlock.objects
                .filter(page=page, is_active=True)
                .order_by('order','id'))

# Массовое добавление времени на трансферы
class BulkTransferScheduleAdmin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("mass-transfer-schedule/", self.admin_site.admin_view(self.bulk_transfer_schedule), name="mass_transfer_schedule")
        ]
        return my_urls + urls

    def bulk_transfer_schedule(self, request):
        if request.method == 'POST':
            form = BulkTransferScheduleForm(request.POST)
            if form.is_valid():
                transfer_type = form.cleaned_data['transfer_type']
                transfer_date = form.cleaned_data['transfer_date']

                for hotel in Hotel.objects.all():
                    time_field = f"time_{hotel.id}"
                    point_field = f"pickup_{hotel.id}"
                    lastname_field = f"lastname_{hotel.id}"  # 🟡 Новое поле

                    time = form.cleaned_data.get(time_field)
                    point = form.cleaned_data.get(point_field)
                    last_name = form.cleaned_data.get(lastname_field)  # 🟡 Получаем фамилию

                    if time and point:
                        TransferSchedule.objects.create(
                            transfer_type=transfer_type,
                            date=transfer_date,
                            hotel=hotel,
                            pickup_point=point,
                            departure_time=time,
                            passenger_last_name=last_name.strip() if last_name else None  # ✅ Сохраняем фамилию
                        )

                self.message_user(request, "Расписание успешно добавлено!")
                return redirect("..")
        else:
            form = BulkTransferScheduleForm()

        return render(request, "admin/bulk_transfer_schedule.html", {
            "form": form,
            "title": "Массовое добавление расписания трансферов",
        })

class TransferScheduleLookupView(APIView):
    def post(self, request):
        serializer = TransferScheduleRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            transfer_type = data['transfer_type']
            hotel_id = data['hotel_id']
            departure_date = data['departure_date']
            last_name = data.get('passenger_last_name', '').strip()

            qs = TransferSchedule.objects.filter(
                transfer_type=transfer_type,
                hotel_id=hotel_id,
                departure_date=departure_date
            )
            if transfer_type == 'private' and last_name:
                qs = qs.filter(passengers__last_name__iexact=last_name)

            transfer = qs.first()
            if not transfer:
                return Response({'error': 'Трансфер не найден'}, status=404)

            pp = transfer.pickup_point or PickupPoint.objects.filter(
                hotel=transfer.hotel, transfer_type=transfer.transfer_type
            ).first()

            if not transfer.departure_time:
                return Response({
                    "success": False,
                    "reason": "time_pending",
                    "message_key": "transfer_time_pending",
                    "pickup_point_name": pp.name if pp else '',
                    "pickup_point_lat": pp.latitude if pp else None,
                    "pickup_point_lng": pp.longitude if pp else None,
                    "hotel_lat": transfer.hotel.latitude,
                    "hotel_lng": transfer.hotel.longitude,
                }, status=200)

            return Response({
                "success": True,
                "departure_time": transfer.departure_time.strftime("%H:%M"),
                "pickup_point_name": pp.name if pp else '',
                "pickup_point_lat": pp.latitude if pp else None,
                "pickup_point_lng": pp.longitude if pp else None,
                "hotel_lat": transfer.hotel.latitude,
                "hotel_lng": transfer.hotel.longitude,
            }, status=200)

        return Response(serializer.errors, status=400)



# Вывод информации о трансфере для туриста
@api_view(['GET'])
def transfer_info(request):
    hotel_id = request.GET.get('hotel_id')
    date = request.GET.get('date')

    if not hotel_id or not date:
        return Response({"error": "Missing hotel_id or date"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        schedule = TransferSchedule.objects.get(hotel_id=hotel_id, departure_date=date)
        pickup = schedule.pickup_point
        return Response({
            "departure_time": schedule.departure_time.strftime("%H:%M"),
            "pickup_point": {
                "name": pickup.name if pickup else "—",
                "latitude": pickup.latitude if pickup else None,
                "longitude": pickup.longitude if pickup else None,
            }
        })
    except TransferSchedule.DoesNotExist:
        return Response({"error": "No transfer found for given hotel and date"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def transfer_schedule_view(request):
    hotel_id = request.GET.get('hotel_id')
    date = request.GET.get('date')
    transfer_type = request.GET.get('type', 'group')
    last_name = request.GET.get('last_name', '').strip().lower()

    if not hotel_id or not date:
        return Response({"error": "Missing hotel_id or date"}, status=400)

    try:
        group = TransferScheduleGroup.objects.filter(
            date=date,
            transfer_type=transfer_type
        ).first()

        if not group:
            return Response({
                "ok": False,
                "message_key": "no_transfer_found"   # ← ключ из вашего translation.json
            }, status=404)

        schedules = group.schedules.filter(hotel_id=hotel_id).order_by('departure_time')

        if not schedules.exists():
            return Response({'error': 'No transfer schedule found'}, status=404)

        # === PRIVATE TRANSFER ===
        if transfer_type == 'private':
            if not last_name:
                return Response({
                    "success": False,
                    "reason": "need_last_name",
                    "message": "Укажите фамилию для получения информации о трансфере."
                }, status=200)

            norm_input = normalize_last_name(last_name)

            # === Точное совпадение по любому пассажиру семьи ===
            exact = (schedules
                     .filter(passengers__last_name__iexact=last_name)
                     .first())
            if exact:
                pp = exact.pickup_point or PickupPoint.objects.filter(
                    hotel=exact.hotel, transfer_type='private'
                ).first()

                # ⬇ NEW: если время ещё не проставлено — возвращаем понятный статус
                if not exact.departure_time:
                    return Response({
                        "success": False,
                        "reason": "time_pending",
                        "message_key": "transfer_time_pending",
                        "pickup_point": pp.name if pp else "—",
                        "pickup_lat": pp.latitude if pp else None,
                        "pickup_lng": pp.longitude if pp else None,
                    }, status=200)

                return Response({
                    "success": True,
                    "pickup_time": exact.departure_time.strftime("%H:%M"),
                    "pickup_point": pp.name if pp else "—",
                    "pickup_lat": pp.latitude if pp else None,
                    "pickup_lng": pp.longitude if pp else None,
                }, status=200)


            # === Fuzzy: пробегаем ВСЕ фамилии пассажиров этих семей ===
            # (собираем один список фамилий)
            from core.models import TransferPassenger
            fams = list(
                TransferPassenger.objects
                .filter(schedule__in=schedules.values("id"))
                .values_list("last_name", flat=True)
            )

            candidates = []
            for ln in fams:
                if not ln:
                    continue
                dist = levenshtein_distance(norm_input, normalize_last_name(ln))
                if 0 < dist <= 3:
                    candidates.append((dist, ln))
            if candidates:
                candidates.sort()
                return Response({
                    "success": False,
                    "reason": "no_exact_match",
                    "suggestion": candidates[0][1]
                })

            return Response({
                "success": False,
                "reason": "not_found",
                "message": "Фамилия не найдена. Проверьте правильность написания."
            })


            if schedules.count() > 1:
                return Response({
                    "success": False,
                    "reason": "multiple_transfers",
                    "message": "Из этого отеля выезжает несколько семей. Укажите фамилию."
                })

            ts = schedules.first()
            pp = ts.pickup_point or PickupPoint.objects.filter(
                hotel=ts.hotel,
                transfer_type='private'
            ).first()
            latitude = pp.latitude if pp else ts.hotel.latitude
            longitude = pp.longitude if pp else ts.hotel.longitude
            pickup_name = pp.name if pp else ts.hotel.name
            return Response({
                "success": True,
                "pickup_time": ts.departure_time.strftime("%H:%M"),
                "pickup_point": pickup_name,
                "pickup_lat": latitude,
                "pickup_lng": longitude,
            })

        # === GROUP TRANSFER ===
        else:
            # Найдём хотя бы один трансфер
            ts = schedules.first()
            pp = ts.pickup_point if ts and ts.pickup_point else PickupPoint.objects.filter(hotel_id=hotel_id, transfer_type='group').first()

            if not ts:
                return Response({'error': 'No transfer schedule found'}, status=404)

            # ⬇ NEW: если времени нет — возвращаем понятный статус (и не форматируем None)
            if not ts.departure_time:
                return Response({
                    "success": False,
                    "reason": "time_pending",
                    "message_key": "group_transfer_time_pending",
                    "pickup_point": pp.name if pp else "—",
                    "pickup_lat": pp.latitude if pp else None,
                    "pickup_lng": pp.longitude if pp else None,
                }, status=200)

            return Response({
                "success": True,
                "pickup_time": ts.departure_time.strftime("%H:%M"),
                "pickup_point": pp.name if pp else "—",
                "pickup_lat": pp.latitude if pp else None,
                "pickup_lng": pp.longitude if pp else None,
            }, status=200)



    except Exception as e:
        return Response({"error": str(e)}, status=500)





@api_view(['GET'])
def available_hotels_for_transfer(request):
    date_str = request.GET.get('date')
    transfer_type = request.GET.get('type', 'group')  # default = group

    if not date_str:
        return Response({"error": "Missing date parameter"}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    hotel_ids = TransferSchedule.objects.filter(
        departure_date=date,
        transfer_type=transfer_type
    ).values_list('hotel_id', flat=True).distinct()

    hotels = Hotel.objects.filter(id__in=hotel_ids)
    serializer = SimpleHotelSerializer(hotels, many=True)
    return Response(serializer.data)


class TransferNotificationViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = TransferNotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()

            group = TransferScheduleGroup.objects.filter(
                date=instance.departure_date,
                transfer_type__iexact=instance.transfer_type
            ).first()

            transfer_item = None
            pickup_point = None

            if group:
                schedules = TransferSchedule.objects.filter(
                    group=group,
                    hotel=instance.hotel
                )

                if instance.transfer_type == 'private':
                    # ⛔ Обязательно указание фамилии
                    if not instance.last_name:
                        return Response({
                            "detail": "Для индивидуального трансфера требуется указать фамилию.",
                            "status": "missing_last_name"
                        }, status=400)

                    # Печать всех фамилий (для отладки)
                    print("== ВСЕ ФАМИЛИИ В БАЗЕ ==")
                    for s in schedules:
                        for p in s.passengers.all():
                            print(f"[БД]: '{p.last_name.strip().lower()}'")
                    print(f"[ИЩЕМ]: '{instance.last_name.strip().lower()}'")

                    # Поиск по любому пассажиру семьи
                    transfer_item = schedules.filter(
                        passengers__last_name__iexact=instance.last_name.strip()
                    ).first()

                    if not transfer_item:
                        return Response({
                            "detail": "Фамилия не найдена в списке трансферов на эту дату.",
                            "status": "not_found"
                        }, status=404)

                else:
                    # ✅ Групповой трансфер — фамилия не обязательна
                    transfer_item = schedules.order_by("departure_time").first()

                # 📍 Точка сбора
                if transfer_item and transfer_item.pickup_point:
                    pickup_point = transfer_item.pickup_point
                else:
                    pickup_point = PickupPoint.objects.filter(
                        hotel=instance.hotel,
                        transfer_type=instance.transfer_type
                    ).first()

            # 🕒 Время трансфера
            departure_time = transfer_item.departure_time if transfer_item else None
            departure_time_str = departure_time.strftime('%H:%M') if departure_time else _("—")

            # 📌 Название и карта
            pickup_name = pickup_point.name if pickup_point else _("не указана")
            map_link = (
                f"https://www.google.com/maps?q={pickup_point.latitude},{pickup_point.longitude}"
                if pickup_point and pickup_point.latitude and pickup_point.longitude
                else None
            )

            # 🌍 Устанавливаем язык
            activate(instance.language)

            # ✉️ Отправка письма
            send_html_email(
                subject="Airport transfer details",
                to_email=instance.email,
                template_name=f"emails/transfer_notification_{instance.language}.html",
                context={
                    "hotel_name": instance.hotel.name,
                    "departure_date": instance.departure_date.strftime('%d.%m.%Y'),
                    "departure_time": departure_time_str,
                    "pickup_point": pickup_name,
                    "map_link": map_link,
                }
            )

            # 💾 Лог отправки
            if departure_time:
                instance.departure_time_sent = departure_time
                instance.save(update_fields=["departure_time_sent"])

            return Response({"detail": _("Информация отправлена на почту.")}, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET'])
def confirm_transfer_notification(request, token):
    try:
        notif = TransferNotification.objects.get(confirmation_token=token)
        notif.is_confirmed = True
        notif.save()
        return render(request, 'confirmation_success.html')  # HTML-шаблон
    except TransferNotification.DoesNotExist:
        return render(request, 'confirmation_error.html')  # HTML-шаблон с ошибкой


@api_view(['POST'])
def notify_transfer_change(request):
    serializer = TransferNotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        send_transfer_update_email(instance)
        return Response({"detail": _("Письмо отправлено с просьбой подтвердить.")})
    return Response(serializer.errors, status=400)

        
# Вьюшка обратной связи по индивидуальтным трансферам
class TransferInquiryViewSet(viewsets.ModelViewSet):
    queryset = TransferInquiry.objects.all()
    serializer_class = TransferInquirySerializer
    http_method_names = ['post']  # только POST для внешнего доступа

    def perform_create(self, serializer):
        inquiry = serializer.save()

        # === Определяем язык письма ===
        supported_languages = ['ru', 'en', 'es', 'lv', 'lt', 'et', 'uk']
        lang = inquiry.language if inquiry.language in supported_languages else 'ru'
        template_name = f"emails/transfer_reply_{lang}.html"

        # === Контекст шаблона ===
        context = {
            'name': inquiry.last_name,
            'hotel': inquiry.hotel.name if inquiry.hotel else '—',
            'date': inquiry.departure_date,
            'flight': inquiry.flight_number or '—',
            'reply': '',  # или текст по умолчанию, если нужно
        }

        html_content = render_to_string(template_name, context)
        text_content = (
            f"Уважаемый(ая) {inquiry.last_name},\n\n"
            f"Мы получили ваш запрос по трансферу.\n"
            f"Дата: {inquiry.departure_date}\n"
            f"Отель: {inquiry.hotel.name if inquiry.hotel else '—'}\n"
            f"Номер рейса: {inquiry.flight_number or '—'}\n\n"
            f"Мы свяжемся с вами в ближайшее время."
        )

        # === Отправка письма ===
        email = EmailMultiAlternatives(
            subject="Your request has been accepted",
            body=text_content,
            from_email="CostaSolinfo.Malaga@gmail.com",
            to=[inquiry.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()


# class QuestionView(RetrieveAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer

#     def get_object(self):
#         return self.queryset.first()

class ContactFormThrottle(AnonRateThrottle):
    rate = '5/min'  # простая защита от спама

class QuestionCreateAPIView(APIView):
    throttle_classes = [ContactFormThrottle]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def post(self, request, *args, **kwargs):
        handler_signature = "QuestionCreateAPIView-vFinal"

        # 0) берём входящие данные (делаем обычный dict)
        try:
            incoming = request.data
            data = dict(incoming)  # DRF Request.data обычно уже dict
        except Exception:
            # на всякий случай
            data = request.data.copy()

        # 1) язык
        language = (data.get("language") or request.headers.get("Accept-Language") or "ru")[:5]
        data["language"] = language

        # 2) источник (если фронт не прислал)
        data.setdefault("source", "contacts" if "contact-questions" in request.path else "ask")

        # 3) категория
        if data.get("category") not in dict(Question.CATEGORY_CHOICES):
            data["category"] = "other"

        logger.debug("[QuestionCreateAPIView] incoming path=%r content_type=%r data=%r",
                     request.path, request.content_type, incoming)

        if settings.DEBUG and request.GET.get('debug') == '1':
            return Response({
                "handler": handler_signature,
                "incoming": incoming,
                "normalized": data
            }, status=200)

        # 4) сериализация и сохранение
        serializer = QuestionSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        logger.debug("[QuestionCreateAPIView] validated_data=%r", serializer.validated_data)

        obj = serializer.save()
        obj.refresh_from_db(fields=['question', 'language', 'source'])
        logger.debug("[QuestionCreateAPIView] AFTER SAVE: id=%s, source=%s, lang=%s, question=%r",
                     obj.id, obj.source, obj.language, obj.question)

        # 5) страховка: фиксируем оригинал и проверим, не стерлось ли после уведомления
        _orig_q = obj.question

        try:
            send_question_notification(obj, language)  # ВАЖНО: внутри ничего не должно присваивать obj.question
        except Exception as e:
            logger.exception("send_question_notification failed: %s", e)

        # 6) проверка после отправки письма — не стерли ли поле
        obj.refresh_from_db(fields=['question'])
        if (not obj.question) and _orig_q:
            logger.warning("[QuestionCreateAPIView] question cleared during notification; restoring. id=%s", obj.id)
            Question.objects.filter(id=obj.id).update(question=_orig_q)
            obj.question = _orig_q

        return Response({
            "message": "Вопрос успешно отправлен.",
            "id": obj.id,
            "saved_question": obj.question,   # то, что реально лежит в БД
        }, status=status.HTTP_201_CREATED)




class ContactInfoView(RetrieveAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer

    def get_object(self):
        return self.queryset.first()

class AboutUsView(RetrieveAPIView):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        return self.queryset.first()

class TeamMemberListAPIView(ListAPIView):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

class ExcursionView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionSerializer

    def get_object(self):
        return self.queryset.first()  # если только одна экскурсия, иначе делаем ListAPIView

def get_excursion_price(request):
    excursion_id = request.GET.get("excursion")
    hotel_id = request.GET.get("hotel")

    try:
        hotel = Hotel.objects.get(id=hotel_id)
        region = hotel.region
        price = ExcursionRegionPrice.objects.get(excursion_id=excursion_id, region=region)
        return JsonResponse({
            "price_adult": str(price.price_adult),
            "price_child": str(price.price_child),
        })
    except (Hotel.DoesNotExist, ExcursionRegionPrice.DoesNotExist):
        return JsonResponse({"error": "Цена не найдена"}, status=404)

class ExcursionListView(ListAPIView):
    queryset = Excursion.objects.filter(is_active=True)
    serializer_class = ExcursionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ExcursionDetailView(RetrieveAPIView):
    queryset = Excursion.objects.all()
    serializer_class = ExcursionDetailSerializer

def pickup_point_detail(request, pk):
    pickup = get_object_or_404(ExcursionPickupPoint, pk=pk)
    return JsonResponse({
        "id": pickup.id,
        "pickup_point_name": pickup.pickup_point_name,
        "latitude": str(pickup.latitude) if pickup.latitude else None,
        "longitude": str(pickup.longitude) if pickup.longitude else None,
        "pickup_time": pickup.pickup_time.strftime("%H:%M") if pickup.pickup_time else None,
    })

@api_view(['GET'])
def excursion_pickup_view(request, excursion_id):
    hotel_id = request.GET.get("hotel_id")
    if not hotel_id:
        return Response({"error": "hotel_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pickup = ExcursionPickupPoint.objects.get(excursion_id=excursion_id, hotel_id=hotel_id)
    except ExcursionPickupPoint.DoesNotExist:
        return Response({"error": "Pickup point not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "id": pickup.id,
        "name": pickup.pickup_point_name,
        "lat": float(pickup.latitude) if pickup.latitude else None,
        "lng": float(pickup.longitude) if pickup.longitude else None,
        "time": pickup.pickup_time.strftime("%H:%M") if pickup.pickup_time else None,
        "price_adult": pickup.price_adult,
        "price_child": pickup.price_child,
    })

# Поисковая система по отелям
@api_view(['GET'])
def hotel_search(request):
    search = request.GET.get('search', '')
    hotels = Hotel.objects.filter(name__icontains=search).values('id', 'name')[:10]
    return Response(list(hotels))


# Политика конфиденциальности
class PrivacyPolicyView(APIView):
    def get(self, request):
        lang = request.GET.get('lang', 'en')
        try:
            policy = PrivacyPolicy.objects.get(language_code=lang)
            return Response({'content': policy.content})
        except PrivacyPolicy.DoesNotExist:
            return Response({'content': ''})



class ContactThrottle(AnonRateThrottle):
    rate = '5/min'   # простая антиспам-защита

# @api_view(['POST'])
# @throttle_classes([ContactThrottle])
# def contact_questions(request):
#     data = request.data.copy()
#     data.setdefault('source', 'contacts')

#     # ✅ нормализуем текст вопроса из разных возможных полей
#     raw_q = data.get('question') or data.get('message') or data.get('text') or ''
#     data['question'] = str(raw_q).strip() or None

#     # защитимся от «левых» категорий
#     if data.get('category') not in dict(Question.CATEGORY_CHOICES):
#         data['category'] = 'other'

#     # 🔥 добавим обработку языка (иначе язык остаётся "None")
#     language = (data.get('language') or request.headers.get("Accept-Language") or "ru")[:5]
#     data['language'] = language

#     if settings.DEBUG:
#         print('[CONTACT_FORM] incoming:', dict(request.data))
#         print('[CONTACT_FORM] normalized:', data)

#     # ✅ передаём нормализованные данные, а не request.data
#     serializer = QuestionSerializer(data=data, context={'request': request})
#     if serializer.is_valid():
#         obj = serializer.save()
#         return Response({'ok': True, 'id': obj.id}, status=status.HTTP_201_CREATED)

#     return Response({'ok': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)





```

---
## backend/core/serializers.py

```py
import re
import unicodedata
import logging
from core.models import (
    Homepage, Excursion, InfoMeeting, AirportTransfer, 
    Question, ContactInfo, AboutUs, TransferSchedule,
    Hotel, PickupPoint, TransferNotification, TransferInquiry,
    PrivacyPolicy, InfoMeetingScheduleItem, ExcursionContentBlock,
    PageBanner, ExcursionImage, Question, TeamMember, TransferPageContentBlock
    )
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers
from .utils import BaseTranslationSerializer  # путь зависит от твоей структуры проекта

logger = logging.getLogger(__name__)
# лид/трейл-очистка с учётом невидимых пробелов
_TRIM_RE = re.compile(r'^[\s\u00A0\u200B\u200C\u200D\uFEFF]+|[\s\u00A0\u200B\u200C\u200D\uFEFF]+$')

SUPPORTED_LANGS = ('ru','en','es','lt','lv','et','uk')

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
```

---
## backend/core/management/commands/audit_excursion_zones.py

```py
# core/management/commands/audit_excursion_zones.py
from django.core.management.base import BaseCommand
from core.models import Hotel
import pandas as pd
import math

def _norm(s):
    if s is None:
        return ""
    return str(s).strip()

def _to_float(v):
    if v is None: return None
    try:
        s = str(v).strip().replace(",", ".")
        return float(s)
    except Exception:
        return None

def haversine_km(lat1, lon1, lat2, lon2):
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

class Command(BaseCommand):
    help = (
        "Аудит временных зон у отелей: ищет отели, у которых ближайшая точка "
        "какой-то ДРУГОЙ зоны ближе, чем ближайшая точка назначенной зоны."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--excel",
            required=True,
            help="Путь к вашему excursions_template_compact.xlsx (лист 'pickup_points').",
        )
        parser.add_argument(
            "--delta",
            type=float,
            default=0.35,   # км: насколько ближе должна быть «чужая» зона, чтобы сработало предупреждение
            help="Порог (км), на сколько чужая зона должна быть ближе, чтобы пометить как сомнительное (default=0.35 км).",
        )
        parser.add_argument(
            "--far",
            type=float,
            default=2.0,    # км: слишком далеко от любых точек СВОЕЙ зоны
            help="Порог (км) для предупреждения 'слишком далеко от своей зоны' (default=2.0 км).",
        )
        parser.add_argument(
            "--csv",
            help="Если указать путь, выгрузит отчёт в CSV.",
        )

    def handle(self, *args, **opts):
        path = opts["excel"]
        delta_km = float(opts["delta"])
        far_km = float(opts["far"])
        out_csv = opts.get("csv")

        # 1) читаем точки
        try:
            df = pd.read_excel(path, sheet_name="pickup_points")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Не удалось прочитать {path}: {e}"))
            return

        for col in ("pickup_point_name", "zone", "direction"):
            if col not in df.columns:
                self.stderr.write(self.style.ERROR(
                    "Лист 'pickup_points' должен содержать столбцы: pickup_point_name, zone, direction, latitude, longitude"
                ))
                return

        df["pickup_point_name"] = df["pickup_point_name"].map(_norm)
        df["zone"] = df["zone"].map(_norm)
        df["direction"] = df["direction"].map(_norm)
        df["latitude"] = df.get("latitude", None).apply(_to_float)
        df["longitude"] = df.get("longitude", None).apply(_to_float)

        # карта: zone -> список точек (lat, lon, name)
        zone_points = {}
        for _, r in df.iterrows():
            z = _norm(r["zone"])
            name = _norm(r["pickup_point_name"])
            lat = r.get("latitude"); lon = r.get("longitude")
            if not z or not name or lat is None or lon is None:
                continue
            zone_points.setdefault(z, []).append((float(lat), float(lon), name))

        zones_total = len(zone_points)
        self.stdout.write(self.style.NOTICE(f"Найдено зон в Excel: {zones_total}"))

        # 2) проверяем отели
        rows = []
        warn_wrong = 0
        warn_far   = 0
        missing    = 0

        hotels = Hotel.objects.all().select_related("excursion_zone", "region")
        for h in hotels:
            z_assigned = getattr(h.excursion_zone, "name", None)
            if h.latitude is None or h.longitude is None or not z_assigned:
                missing += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned or "",
                    issue="NO_COORDS_OR_ZONE",
                    best_zone="", dist_assigned="", best_dist="",
                    note="Нет координат и/или не назначена временная зона"
                ))
                continue

            lat_h, lon_h = float(h.latitude), float(h.longitude)

            # ближайшая точка своей зоны
            dist_assigned = None
            if z_assigned in zone_points:
                for (lat, lon, _name) in zone_points[z_assigned]:
                    d = haversine_km(lat_h, lon_h, lat, lon)
                    if d is not None:
                        dist_assigned = d if dist_assigned is None else min(dist_assigned, d)

            # ближайшая точка среди всех зон
            best_zone = None
            best_dist = None
            best_name = None
            for z, plist in zone_points.items():
                for (lat, lon, pname) in plist:
                    d = haversine_km(lat_h, lon_h, lat, lon)
                    if d is None:
                        continue
                    if best_dist is None or d < best_dist:
                        best_dist = d
                        best_zone = z
                        best_name = pname

            # кейс 1: своей зоны нет в файле
            if dist_assigned is None:
                warn_wrong += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="ASSIGNED_ZONE_HAS_NO_POINTS",
                    best_zone=best_zone or "", dist_assigned="",
                    best_dist=f"{best_dist:.3f}" if best_dist is not None else "",
                    note=f"В Excel нет точек для назначенной зоны; ближайшая зона: {best_zone} ({best_name})"
                ))
                continue

            # кейс 2: слишком далеко от своей зоны
            if dist_assigned > far_km:
                warn_far += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="FAR_FROM_OWN_ZONE",
                    best_zone=best_zone or "", dist_assigned=f"{dist_assigned:.3f}",
                    best_dist=f"{best_dist:.3f}" if best_dist is not None else "",
                    note=f"До ближайшей точки своей зоны {dist_assigned:.2f} км (> {far_km} км)"
                ))

            # кейс 3: чужая зона заметно ближе своей
            if best_zone and best_dist + delta_km < dist_assigned:
                warn_wrong += 1
                rows.append(dict(
                    hotel=h.name, zone_assigned=z_assigned,
                    issue="LIKELY_WRONG_ZONE",
                    best_zone=best_zone, dist_assigned=f"{dist_assigned:.3f}",
                    best_dist=f"{best_dist:.3f}",
                    note=f"Чужая зона '{best_zone}' ближе на ≥ {delta_km} км (ближайшая точка '{best_name}')"
                ))

        # вывод
        self.stdout.write(self.style.SUCCESS(
            f"Готово. Всего отелей: {hotels.count()}, пропуски: {missing}, "
            f"подозрительные: {warn_wrong}, далеко от своей зоны: {warn_far}."
        ))

        if rows:
            # короткий консольный обзор
            for r in rows[:20]:
                self.stdout.write(
                    f"[{r['issue']}] {r['hotel']}: assigned='{r['zone_assigned']}', "
                    f"best='{r['best_zone']}', dist_assigned='{r['dist_assigned']}', best_dist='{r['best_dist']}' "
                    f"| {r['note']}"
                )

        if out_csv:
            import csv
            with open(out_csv, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=["hotel","zone_assigned","issue","best_zone","dist_assigned","best_dist","note"])
                w.writeheader()
                w.writerows(rows)
            self.stdout.write(self.style.NOTICE(f"Отчёт сохранён: {out_csv}"))

```

---
## frontend/src/index.js

```js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './i18n'; // Добавляем перед рендером App
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

```

---
## frontend/src/App.js

```js
// src/App.js
import React, { useEffect, useState } from 'react';     // ⬅️ добавили useEffect, useState
import './styles/main.css';
import './styles/navbar.css';
import 'leaflet/dist/leaflet.css';

import ExcursionsPage from "./pages/ExcursionsPage";
import ExcursionDetailPage from "./pages/ExcursionDetailPage";

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import HomePage from './pages/HomePage';
import InfoMeetingPage from './pages/InfoMeetingPage';
import AirportTransferChoicePage from './pages/AirportTransferChoicePage';
import AirportTransferGroupPage from './pages/AirportTransferGroupPage';
import AirportTransferPrivatePage from './pages/AirportTransferPrivatePage';
import AskQuestionPage from './pages/AskQuestionPage';
import ContactsPage from './pages/ContactsPage';
import AboutUsPage from './pages/AboutUsPage';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ScrollToTopButton from './components/ScrollToTopButton';
import CookieBanner from './components/CookieBanner';
import PrivacyPolicyModal from './components/PrivacyPolicyModal';  // ⬅️ НОВОЕ

function App() {
  const [openPrivacy, setOpenPrivacy] = useState(false); // ⬅️ НОВОЕ

  // Глобальная функция, чтобы открыть модалку откуда угодно (баннер/футер)
  useEffect(() => {
    window.csiOpenPrivacy = () => setOpenPrivacy(true);
    return () => { delete window.csiOpenPrivacy; };
  }, []);

  return (
    <Router>
      <Navbar />

      <div className="main-container" style={{ padding: '20px' }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/excursions" element={<ExcursionsPage />} />
          <Route path="/excursion/:id" element={<ExcursionDetailPage />} />
          <Route path="/info-meeting" element={<InfoMeetingPage />} />
          <Route path="/airport-transfer" element={<AirportTransferChoicePage />} />
          <Route path="/airport-transfer/group" element={<AirportTransferGroupPage />} />
          <Route path="/airport-transfer/private" element={<AirportTransferPrivatePage />} />
          <Route path="/ask" element={<AskQuestionPage />} />
          <Route path="/contacts" element={<ContactsPage />} />
          <Route path="/about" element={<AboutUsPage />} />
        </Routes>
      </div>

      <CookieBanner />
      <Footer />
      <ScrollToTopButton />

      {/* ⬇️ Модалка политики — монтируется один раз на всём приложении */}
      <PrivacyPolicyModal
        isOpen={openPrivacy}
        onClose={() => setOpenPrivacy(false)}
      />
    </Router>
  );
}

export default App;

```

---
## frontend/src/i18n.js

```js
// src/i18n.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import translationRU from './locales/ru/translation.json';
import translationEN from './locales/en/translation.json';
import translationLT from './locales/lt/translation.json';
import translationLV from './locales/lv/translation.json';
import translationET from './locales/et/translation.json';
import translationUK from './locales/uk/translation.json';
import translationES from './locales/es/translation.json';

const resources = {
  ru: { translation: translationRU },
  en: { translation: translationEN },
  lt: { translation: translationLT },
  lv: { translation: translationLV },
  et: { translation: translationET },
  uk: { translation: translationUK },
  es: { translation: translationES },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ru', // язык по умолчанию
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;

```

---
## frontend/src/pages/HomePage.js

```js
// src/pages/HomePage.jsx
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import './HomePage.css';

const HomePage = () => {
  const { i18n } = useTranslation();
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [bannerImage, setBannerImage] = useState('');

  const defaultImage = '/images/default_excursion.jpg';

  useEffect(() => {
    const ctrl = new AbortController();

    fetch('http://127.0.0.1:8000/api/homepage/', {
      headers: { 'Accept-Language': i18n.language },
      signal: ctrl.signal,
      cache: 'no-store',
    })
      .then(res => res.json())
      .then(data => {
        const lang = i18n.language;

        // ✅ сперва локализованные поля (если BaseTranslationSerializer уже выдал их),
        // затем fallbacks на явные *_<lang>, и в конце на русский как запасной
        const resolvedTitle =
          data?.title ??
          data?.[`title_${lang}`] ??
          data?.title_ru ??
          '';

        const resolvedSubtitle =
          data?.subtitle ??
          data?.[`subtitle_${lang}`] ??
          data?.subtitle_ru ??
          '';

        setTitle(resolvedTitle);
        setSubtitle(resolvedSubtitle);

        let imageUrl = defaultImage;
        if (data?.banner_image && typeof data.banner_image === 'string') {
          imageUrl = data.banner_image.startsWith('http')
            ? data.banner_image
            : `http://127.0.0.1:8000${data.banner_image}`;
        }
        setBannerImage(imageUrl);
      })
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error('Ошибка загрузки главной страницы:', err);
          setBannerImage(defaultImage);
        }
      });

    return () => ctrl.abort();
  }, [i18n.language]);

  return (
    <>
      {/* Баннер как на других страницах (если нужен image из админки — допиши проп imageUrl={bannerImage} в сам компонент PageBanner) */}
      <PageBanner page="home" />

      <div className="page-container">
        {/* Если нужно — можно отрисовать и заголовок */}
        {title && <h1 style={{ marginBottom: 12 }}>{title}</h1>}

        {/* ВАЖНО: рендерим HTML из админки с форматированием */}
        <div
          className="homepage-subtitle"
          dangerouslySetInnerHTML={{ __html: subtitle || '' }}
        />
      </div>
    </>
  );
};

export default HomePage;

```

---
## frontend/src/pages/ExcursionsPage.js

```js
// src/pages/ExcursionsPage.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import "../styles/ExcursionsPage.css";
import Breadcrumbs from "../components/Breadcrumbs";

const ExcursionsPage = () => {
  const { t, i18n } = useTranslation();
  const [excursions, setExcursions] = useState([]);
  const [loading, setLoading] = useState(true);

  const defaultImage = "/images/default_excursion.jpg";

  useEffect(() => {
    axios
      .get("/api/excursions/", { headers: { "Accept-Language": i18n.language } })
      .then(res => { setExcursions(res.data || []); })
      .catch(err => { console.error("Ошибка загрузки экскурсий:", err); })
      .finally(() => setLoading(false));
  }, [i18n.language]);

  if (loading) return <p>{t("loading")}</p>;
  if (!excursions || excursions.length === 0) return <p>{t("no_excursions_found")}</p>;

  return (
    <>
      <PageBanner page="excursions" />

      <div className="page-container">
        <Breadcrumbs
          items={[
            { to: "/", label: t("home") },
            { label: t("excursions") },
          ]}
        />

        <h2 style={{ textAlign: "center", marginBottom: 20 }}>
          {t("excursions")}
        </h2>

        <div className="excursions-list">
          {excursions.map((excursion) => {
            let imageUrl = defaultImage;
            if (excursion && typeof excursion.image === "string" && excursion.image.length > 0) {
              imageUrl = excursion.image.startsWith("http")
                ? excursion.image
                : `http://127.0.0.1:8000${excursion.image}`;
            }

            const introText = excursion.localized_description
              ? excursion.localized_description.replace(/<\/?[^>]+(>|$)/g, "").slice(0, 120) + "…"
              : "";

            return (
              <div key={excursion.id} className="excursion-card">
                <img
                  src={imageUrl}
                  alt={excursion.localized_title || t("excursion")}
                  className="excursion-thumb"
                  onError={(e) => { e.currentTarget.src = defaultImage; }}
                />

                <h2>{excursion.localized_title || t("excursion")}</h2>

                {introText && <p className="excursion-intro">{introText}</p>}

                <Link to={`/excursion/${excursion.id}`}>{t("read_more")}</Link>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default ExcursionsPage;

```

---
## frontend/src/pages/ExcursionDetailPage.js

```js
import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";
import PageBanner from "../components/PageBanner";
import PickupMap from "../components/PickupMap";
import "../styles/ExcursionDetailPage.css";
import Breadcrumbs from "../components/Breadcrumbs";

const ExcursionDetailPage = () => {
  const { id } = useParams();
  const { i18n, t } = useTranslation();
  const [excursion, setExcursion] = useState(null);
  const [hotelQuery, setHotelQuery] = useState("");
  const [hotelOptions, setHotelOptions] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [pickupInfo, setPickupInfo] = useState(null);
  const [error, setError] = useState("");
  const mapRef = useRef(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showArrows, setShowArrows] = useState(false);
  

  let hideTimeout = null;

  const handleGalleryTap = () => {
    setShowArrows(true);

    // скрыть через 3 секунды
    if (hideTimeout) clearTimeout(hideTimeout);
    hideTimeout = setTimeout(() => setShowArrows(false), 3000);
  };


  const openModal = (index) => {
    setCurrentIndex(index);
    setModalOpen(true);
  };

  const closeModal = () => setModalOpen(false);

  const prevImage = () => {
    setCurrentIndex((prev) => (prev === 0 ? excursion.images.length - 1 : prev - 1));
  };

  const nextImage = () => {
    setCurrentIndex((prev) => (prev === excursion.images.length - 1 ? 0 : prev + 1));
  };
  


  // Загружаем экскурсию
  useEffect(() => {
    axios
      .get(`/api/excursions/${id}/`, {
        headers: { "Accept-Language": i18n.language },
      })
      .then((res) => setExcursion(res.data))
      .catch((err) => console.error("Ошибка загрузки экскурсии:", err));
  }, [id, i18n.language]);

  // Поиск отелей
  useEffect(() => {
    if (hotelQuery.length < 2 || selectedHotel?.name === hotelQuery) {
      setHotelOptions([]);
      return;
    }

    const delayDebounce = setTimeout(() => {
      axios
        .get(`/api/hotels/?search=${hotelQuery}`)
        .then((res) => setHotelOptions(res.data))
        .catch(() => setHotelOptions([]));
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [hotelQuery, selectedHotel]);


  // Выбор отеля
  const handleSelectHotel = (hotel) => {
    setSelectedHotel({
      ...hotel,
      lat: hotel.latitude ? Number(hotel.latitude) : null,
      lng: hotel.longitude ? Number(hotel.longitude) : null,
    });
    setHotelQuery(hotel.name);
    setHotelOptions([]);
    //setPickupInfo(null);

    // убираем фокус с input, чтобы список исчез сразу
    document.getElementById("hotel-input").blur();

    axios
      .get(`/api/excursions/${id}/pickup/?hotel_id=${hotel.id}`)
      .then((res) => {
        if (res.data && res.data.lat != null && res.data.lng != null) {
          setPickupInfo({
            ...res.data,
            lat: res.data.lat ? Number(res.data.lat) : null,
            lng: res.data.lng ? Number(res.data.lng) : null,
            name: res.data.name || hotel.name,
            time: res.data.time || null,
            adult_price: res.data.price_adult || null,
            child_price: res.data.price_child || null,
          });
          setError("");
          // 🔹 прокрутка к карте
          setTimeout(() => {
            if (mapRef.current) {
              mapRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
            }
          }, 300);
        } else {
          setPickupInfo(null);
          setError(t("no_excursion_for_hotel"));
        }
      })
      .catch(() => {
        setPickupInfo(null);
        setError(t("no_excursion_for_hotel"));
      });
  };

  if (!excursion) return <p>{t("loading")}</p>;

  return (
    <>
      <PageBanner page="excursions" />
      <div className="page-container">
        <Breadcrumbs items={[
            { to: "/", label: t("home") },
            { to: "/excursions", label: t("excursions") },
            { label: excursion?.title || "…" }
          ]}/>
        <div className="excursion-detail-container">
          <h1>{excursion.localized_title}</h1>

          {/* Фотогалерея */}
          {excursion.images?.length > 0 && (
            <div
              className={`excursion-gallery-container ${showArrows ? "show-arrows" : ""}`}
              onClick={handleGalleryTap}
            >
              <button
                className="gallery-arrow left"
                onClick={(e) => {
                  e.stopPropagation();
                  document.querySelector(".excursion-gallery").scrollBy({ left: -300, behavior: "smooth" });
                }}
              >
                ‹
              </button>
              <div className="excursion-gallery">
                {excursion.images.map((img, idx) => (
                  <img
                    key={idx}
                    src={img}
                    alt={`Фото ${idx + 1}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      openModal(idx);
                    }}
                  />
                ))}
              </div>
              <button
                className="gallery-arrow right"
                onClick={(e) => {
                  e.stopPropagation();
                  document.querySelector(".excursion-gallery").scrollBy({ left: 300, behavior: "smooth" });
                }}
              >
                ›
              </button>
            </div>
          )}



          {modalOpen && (
            <div className="modal" onClick={closeModal}>
              <span className="close-btn" onClick={closeModal}>×</span>
              <span className="modal-arrow left" onClick={(e) => { e.stopPropagation(); prevImage(); }}>‹</span>
              <img src={excursion.images[currentIndex]} alt={`Фото ${currentIndex + 1}`} />
              <span className="modal-arrow right" onClick={(e) => { e.stopPropagation(); nextImage(); }}>›</span>
            </div>
          )}




          {/* Основной контент */}
          <div className="excursion-content">
            {excursion.content_blocks?.map((block, idx) => (
              <div key={idx} className="excursion-block">
                <h2>{block.localized_title}</h2>
                <div dangerouslySetInnerHTML={{ __html: block.localized_content }} />
              </div>
            ))}
          </div>

          

          {/* Блок выбора отеля */}
          <div className="hotel-select-block">
            <h3 className="hotel-title">🚍 {t("excursion.select_hotel_title")}</h3>
            {/*<p className="hotel-instruction">{t("excursion.select_hotel_instruction")}</p>*/}

            <div className="hotel-select">
              <label htmlFor="hotel-input" className="hotel-label">
                {t("choose_your_hotel")}
              </label>
              <input
                id="hotel-input"
                type="text"
                value={hotelQuery}
                autoComplete="off"
                onChange={(e) => {
                  setHotelQuery(e.target.value);
                  setSelectedHotel(null);
                }}
                placeholder={t("excursion.select_hotel_placeholder")}
              />
              {hotelOptions.length > 0 && (
                <ul>
                  {hotelOptions.map((hotel) => (
                    <li
                      key={hotel.id}
                      onClick={() => {
                        handleSelectHotel(hotel);
                        setHotelOptions([]); // очистить список
                        document.getElementById("hotel-input").blur(); // убрать фокус
                      }}
                    >
                      {hotel.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>



          {/* Карта с точкой сбора */}
          {pickupInfo && (
            <div ref={mapRef} className="pickup-section">
              {/* Время и цены */}
              <div className="pickup-details">
                <p className="pickup-time">
                  ⏰ {t("excursion_pickup_time")}: <span>{pickupInfo.time}</span>
                </p>

                {(pickupInfo.adult_price || pickupInfo.child_price) && (
                  <div className="excursion-prices">
                    {pickupInfo.adult_price && (
                      <p className="price-adult">
                        💶 {t("adult_price")}: {pickupInfo.adult_price} €
                      </p>
                    )}
                    {pickupInfo.child_price && (
                      <>
                        <p className="price-child">
                          👧 {t("child_price")}: {pickupInfo.child_price} €
                        </p>
                        <p className="child-note">
                          {t("excursion.child_free_note")}
                        </p>
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* Заголовок по центру */}
              <h3 className="pickup-title">{t("pickup_point")}</h3>

              {/* Карта */}
              <PickupMap hotel={selectedHotel} pickupPoint={pickupInfo} />

              {/* Кнопка Google Maps под картой слева */}
              {pickupInfo.lat && pickupInfo.lng && (
                <div className="google-maps-button-container">
                  <a
                    href={`https://www.google.com/maps?q=${pickupInfo.lat},${pickupInfo.lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="book-button"
                  >
                    📍 {t("open_in_google_maps")}
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Сообщение об ошибке */}
          {error && (
            <p style={{ color: "red", textAlign: "center", marginTop: "10px" }}>
              {error}
            </p>
          )}

          {/* Временно скрыли кнопку */}
          {false && (
            <button
              className="book-button"
              disabled={!selectedHotel || !pickupInfo}
            >
              {t("show_info")}
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default ExcursionDetailPage;

```

---
## frontend/src/pages/AirportTransferPage.js

```js
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import MapComponent from '../components/MapComponent';

const AirportTransferPage = () => {
  const { t, i18n } = useTranslation();

  const [transferType, setTransferType] = useState('group');
  const [hotelId, setHotelId] = useState('');
  const [departureDate, setDepartureDate] = useState(null);
  const [lastName, setLastName] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);

    const body = {
      transfer_type: transferType,
      hotel_id: parseInt(hotelId),
      departure_date: departureDate?.toISOString().split('T')[0],
      passenger_last_name: transferType === 'private' ? lastName : '',
    };

    try {
      const response = await fetch('/api/transfer-schedule/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const err = await response.json();
        setError(err.error || 'Transfer not found');
      }
    } catch (err) {
      setError('Ошибка соединения с сервером');
    }
  };

  return (
    <div className="page">
      <h1>Трансфер в аэропорт</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>
            <input type="radio" value="group" checked={transferType === 'group'} onChange={() => setTransferType('group')} />
            Групповой трансфер
          </label>
          <label>
            <input type="radio" value="private" checked={transferType === 'private'} onChange={() => setTransferType('private')} />
            Индивидуальный трансфер
          </label>
        </div>

        <div>
          <label>Отель (ID):</label>
          <input type="number" value={hotelId} onChange={(e) => setHotelId(e.target.value)} required />
        </div>

        <div>
          <label>Дата вылета:</label>
          <DatePicker
            selected={departureDate}
            onChange={(date) => setDepartureDate(date)}
            dateFormat="yyyy-MM-dd"
            placeholderText="Выберите дату"
          />
        </div>

        {transferType === 'private' && (
          <div>
            <label>Фамилия:</label>
            <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} />
          </div>
        )}

        <button type="submit">Показать трансфер</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div style={{ marginTop: '20px' }}>
          <h3>Информация о трансфере:</h3>
          <p><strong>Время выезда:</strong> {result.departure_time}</p>
          <p><strong>Точка сбора:</strong> {result.pickup_point_name}</p>

          {result.pickup_point_lat && result.pickup_point_lng && (
            <MapComponent lat={result.pickup_point_lat} lng={result.pickup_point_lng} />
          )}
        </div>
      )}
    </div>
  );
};

export default AirportTransferPage;

```

---
## frontend/src/pages/AirportTransferGroupPage.js

```js
// frontend/src/pages/AirportTransferGroupPage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import DatePicker from 'react-datepicker';
import TransferMap from '../components/TransferMap';
import PrivacyPolicyModal from '../components/PrivacyPolicyModal';
import 'react-datepicker/dist/react-datepicker.css';
import Button from '../components/Button';
import TransferContent from '../components/TransferContent';
import Breadcrumbs from "../components/Breadcrumbs";

const getIsoDate = (d) => {
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().split('T')[0];
};

const textFromApi = (t, data) =>
  t(data?.message_key || data?.error_key || 'something_went_wrong');


const AirportTransferGroupPage = () => {
  const { t, i18n } = useTranslation();
  const [hotel, setHotel] = useState('');
  const [hotelId, setHotelId] = useState(null);
  const [hotelSuggestions, setHotelSuggestions] = useState([]);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [date, setDate] = useState(null);
  const [pickupTime, setPickupTime] = useState('');
  const [pickupPoint, setPickupPoint] = useState('');
  const [pickupCoords, setPickupCoords] = useState(null);

  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [inquiryLastName, setInquiryLastName] = useState('');
  const [inquiryHotel, setInquiryHotel] = useState('');
  const [inquiryDate, setInquiryDate] = useState(null);
  const [inquiryFlight, setInquiryFlight] = useState('');
  const [inquiryMessage, setInquiryMessage] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquirySuccessMessage, setInquirySuccessMessage] = useState('');
  const [inquiryError, setInquiryError] = useState('');
  const [inquiryHotelSuggestions, setInquiryHotelSuggestions] = useState([]);
  const [inquiryHotelId, setInquiryHotelId] = useState(null);
  const [inquirySuggestionsVisible, setInquirySuggestionsVisible] = useState(false);

  const [email, setEmail] = useState('');
  const [subscriberLastName, setSubscriberLastName] = useState('');
  const [checkboxAccepted, setCheckboxAccepted] = useState(false);
  const [emailSentMessage, setEmailSentMessage] = useState('');
  const [showPolicyModal, setShowPolicyModal] = useState(false);

  const [error, setError] = useState('');

  // 🔹 Загрузка отелей при вводе
  useEffect(() => {
    if (hotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${hotel}`)
        .then((res) => res.json())
        .then((data) => {
          setHotelSuggestions(data);
          setSuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей:', err));
    } else {
      setHotelSuggestions([]);
      setSuggestionsVisible(false);
    }
  }, [hotel]);

  // 🔹 Выбор отеля из подсказки
  const handleSelectHotel = (name, id) => {
    setHotel(name);
    setHotelId(id);
    setHotelSuggestions([]);
    setSuggestionsVisible(false);
    setTimeout(() => {
      document.activeElement.blur();
    }, 0);
  };


  // 🔹 Отправка формы
  const handleSubmit = async (e) => {
    e.preventDefault();
    setInquirySuccessMessage('');
    setInquiryError('');

    if (!hotelId || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const dateStr = getIsoDate(date);
      const url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=group`;

      const response = await fetch(url);
      const data = await response.json();

      if (response.ok) {
        // время ещё не назначено
        if (data?.success === false && data?.reason === 'time_pending') {
          setPickupTime('');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setShowInquiryForm(true);                  // ← показываем форму
          setError(textFromApi(t, data));            // текст по ключу
          return;
        }

        // успешный ответ
        if (data?.success === true) {
          setPickupTime(data.pickup_time || '');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setError('');
          setShowInquiryForm(false);
          return;
        }

        // fallback
        setPickupTime('');
        setPickupPoint('');
        setPickupCoords(null);
        setShowInquiryForm(true);
        setError(textFromApi(t, data));
        return;
      }

      // НЕ ok (404/400/…)
      setPickupTime('');
      setPickupPoint('');
      setPickupCoords(null);

      if (data?.error_key || data?.message_key) {
        setError(textFromApi(t, data));
        if (data?.error_key === 'no_transfer_found' || data?.message_key === 'no_transfer_found') {
          setShowInquiryForm(true);
        }
      } else if (typeof data?.error === 'string' && data.error.toLowerCase().includes('no transfer')) {
        setError(t('no_transfer_found_message'));
        setShowInquiryForm(true);
      } else {
        setError(t('something_went_wrong'));
      }
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
    }
  };


  const handleInquirySubmit = async (e) => {
    e.preventDefault();

    if (!inquiryLastName || !inquiryHotelId || !inquiryDate || !inquiryEmail) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const localDate = new Date(inquiryDate.getTime() - inquiryDate.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-inquiries/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          last_name: inquiryLastName.trim(),
          hotel: inquiryHotelId,
          departure_date: dateStr,
          flight_number: inquiryFlight.trim(),
          message: inquiryMessage.trim(),
          email: inquiryEmail.trim(),
          language: i18n.language, // ⬅️ ВАЖНО: добавляем текущий язык
        }),
      });

      if (response.ok) {
        setInquirySuccessMessage(t('request_sent_successfully'));

        setInquiryLastName('');
        setInquiryHotel('');
        setInquiryDate(null);
        setInquiryFlight('');
        setInquiryMessage('');
        setInquiryEmail('');
        setError('');
        setShowInquiryForm(false);
      } else {
        const data = await response.json();
        console.error('Ошибка запроса:', data);
        setError(t('request_error'));
      }
    } catch (err) {
      console.error('Ошибка соединения:', err);
      setError(t('request_error'));
    }
  };

  useEffect(() => {
    if (inquiryHotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${inquiryHotel}`)
        .then((res) => res.json())
        .then((data) => {
          setInquiryHotelSuggestions(data);
          setInquirySuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей для запроса:', err));
    } else {
      setInquiryHotelSuggestions([]);
      setInquirySuggestionsVisible(false);
    }
  }, [inquiryHotel]);

  const handleSelectInquiryHotel = (name, id) => {
    setInquiryHotel(name);
    setInquiryHotelId(id);
    setInquiryHotelSuggestions([]);
    setInquirySuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0);
  };



  // Отправка писем об изменении трансфера и их подписки
  const handleEmailSubmit = async () => {
    if (!email || !checkboxAccepted || !hotelId || !date) return;

    try {
      const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-notifications/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          hotel: hotelId,  // ✅ Важно: заменили hotel_id на hotel
          transfer_type: 'group',
          departure_date: dateStr,
          language: i18n.language,
          last_name: subscriberLastName.trim(), // ⬅️ добавили фамилию
        })
      });

      if (response.ok) {
        setEmailSentMessage(t('email_sent_success'));
        setEmail('');
        setCheckboxAccepted(false);
      } else {
        const data = await response.json();
        console.error('Ошибка отправки:', data);
        setEmailSentMessage(t('email_send_error'));
      }
    } catch (err) {
      console.error(err);
      setEmailSentMessage(t('email_send_error'));
    }
  };

  const isValidEmail = (email) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);





  return (
    <>
      <PageBanner page="group_transfer" />
        

      
      <div className="page-container">

      <Breadcrumbs items={[
          { to: "/", label: t("home") },
          { to: "/airport-transfer", label: t("airport_transfer") },
          { label: t("group_transfer") } // или t("private_transfer")
        ]}/>

      <TransferContent page="transfer_group" />
        
        <h1>{t('group_transfer')}</h1>
        <p>{t('enter_hotel_and_date')}</p>

        <form onSubmit={handleSubmit} className="transfer-form left-aligned">
          {/* 🔹 Отель */}
          <label>{t('enter_hotel')}</label>
          <div className="autocomplete-wrapper">
            <input
              type="text"
              value={hotel}
              onChange={(e) => setHotel(e.target.value)}
              placeholder={t('enter_hotel')}
              className="transfer-input"
            />
            {hotelSuggestions.length > 0 && !hotelSuggestions.some(h => h.name === hotel) && (
              <ul className="autocomplete-list">
                {hotelSuggestions.map((item) => (
                  <li key={item.id} onMouseDown={() => handleSelectHotel(item.name, item.id)}>
                    {item.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* 🔹 Дата */}
          <label>{t('select_date')}</label>
          <DatePicker
            selected={date}
            onChange={(date) => setDate(date)}
            placeholderText={t('select_date')}
            className="transfer-input"
            dateFormat="yyyy-MM-dd"
          />

          {/* 🔹 Кнопка */}
          <button
            type="submit"
            className="transfer-button"
            style={{ alignSelf: "flex-start" }}
          >
            {t('show_transfer_time')}
          </button>

        </form>

        {/* 🔹 Ошибка */}
        {error && (
          <div className="transfer-warning-box">
            {error}
          </div>
        )}

        {inquirySuccessMessage && !pickupTime && (
          <div className="success-message-box">
            {inquirySuccessMessage}
          </div>
        )}

        {showInquiryForm && (
          <form onSubmit={handleInquirySubmit} className="transfer-form left-aligned" style={{ marginTop: '30px' }}>
            <h3>{t('not_found_contact_us')}</h3>

            {/* для групповых фамилия не обязательна — можешь убрать это поле */}
            <label>{t('your_last_name')}</label>
            <input
              type="text"
              value={inquiryLastName}
              onChange={(e) => setInquiryLastName(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_hotel')}</label>
            <div className="autocomplete-wrapper">
              <input
                type="text"
                value={inquiryHotel}
                onChange={(e) => setInquiryHotel(e.target.value)}
                placeholder={t('your_hotel')}
                className="transfer-input"
              />
              {inquiryHotelSuggestions.length > 0 && !inquiryHotelSuggestions.some(h => h.name === inquiryHotel) && (
                <ul className="autocomplete-list">
                  {inquiryHotelSuggestions.map((item) => (
                    <li key={item.id} onMouseDown={() => handleSelectInquiryHotel(item.name, item.id)}>
                      {item.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <label>{t('departure_date')}</label>
            <DatePicker
              selected={inquiryDate}
              onChange={(date) => setInquiryDate(date)}
              placeholderText={t('select_date')}
              className="transfer-input"
              dateFormat="yyyy-MM-dd"
            />

            <label>{t('flight_number')}</label>
            <input
              type="text"
              value={inquiryFlight}
              onChange={(e) => setInquiryFlight(e.target.value)}
              className="transfer-input"
            />

            <label>{t('question')}</label>
            <textarea
              value={inquiryMessage}
              onChange={(e) => setInquiryMessage(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_email')}</label>
            <input
              type="email"
              value={inquiryEmail}
              onChange={(e) => setInquiryEmail(e.target.value)}
              className="transfer-input"
            />

            <Button className="transfer-button" style={{ marginTop: '15px' }}>
              {t('send_request')}
            </Button>
          </form>
        )}

        
        {/* 🔹 Результат */}
        {pickupTime && (
          <div className="transfer-result">
            <h3>{t('pickup_time')}:</h3>
            <p>{pickupTime}</p>
            {pickupPoint && <p>{t('pickup_point')}: {pickupPoint}</p>}

            {/* 🔹 Вставляем карту только если есть координаты */}
            {pickupCoords && (
              <div style={{ height: '400px', marginTop: '20px' }}>
                <TransferMap
                  lat={pickupCoords.lat}
                  lng={pickupCoords.lng}
                  pickupName={pickupPoint}
                />
              </div>
            )}

            {inquirySuccessMessage && (
              <p style={{ marginTop: '15px', color: 'green' }}>{inquirySuccessMessage}</p>
            )}
            {inquiryError && (
              <p style={{ marginTop: '15px', color: 'red' }}>{inquiryError}</p>
            )}


            {/* 🔹 Форма для email */}
            {pickupTime && (
              <div className="email-subscription" style={{ marginTop: '30px' }}>
                <h3>{t('want_to_receive_email')}</h3>
                <p>{t('email_info_text')}</p>

                {/* 📨 Email */}
                <div style={{ maxWidth: '320px', margin: '0 auto', textAlign: 'left' }}>
                  <label
                    style={{
                      fontWeight: 'bold',
                      display: 'block',
                      marginBottom: '6px'
                    }}
                  >
                    {t('enter_your_email_label')}
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t('enter_email')}
                    className="transfer-input"
                    required
                  />
                </div>

                {/* 👤 Фамилия */}
                <div style={{ maxWidth: '320px', margin: '15px auto 0', textAlign: 'left' }}>
                  <label
                    style={{
                      fontWeight: 'bold',
                      display: 'block',
                      marginBottom: '6px'
                    }}
                  >
                    {t('enter_your_lastname_label')}
                  </label>
                  <input
                    type="text"
                    value={subscriberLastName}
                    onChange={(e) => setSubscriberLastName(e.target.value)}
                    placeholder={t('your_last_name')}
                    className="transfer-input"
                    required
                  />
                </div>

                {/* ✅ Checkbox */}
                <div style={{ marginTop: '10px' }}>
                  <input
                    type="checkbox"
                    checked={checkboxAccepted}
                    onChange={(e) => setCheckboxAccepted(e.target.checked)}
                    id="consent"
                    onClick={(e) => e.stopPropagation()} // не даёт всплытию перейти к label
                  />
                  <label
                    htmlFor="consent"
                    style={{ marginLeft: '8px', cursor: 'pointer' }}
                    onClick={() => setShowPolicyModal(true)}
                  >
                    {t('i_agree_with')}{' '}
                    <span style={{ color: 'blue', textDecoration: 'underline' }}>
                      {t('terms_and_privacy')}
                    </span>
                  </label>
                </div>

                <PrivacyPolicyModal
                  isOpen={showPolicyModal}
                  onClose={() => setShowPolicyModal(false)}
                />

                {/* 📩 Кнопка */}
                <Button
                  onClick={handleEmailSubmit}
                  className="transfer-button"
                  style={{
                    marginTop: '20px',
                    backgroundColor: (!checkboxAccepted || !isValidEmail(email) || !subscriberLastName) ? '#ccc' : '#00aaff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    fontSize: '16px',
                    cursor: (!checkboxAccepted || !isValidEmail(email) || !subscriberLastName) ? 'not-allowed' : 'pointer',
                    transition: '0.3s ease',
                  }}
                  disabled={!checkboxAccepted || !isValidEmail(email) || !subscriberLastName}
                >
                  {t('send_to_email')}
                </Button>


                {emailSentMessage && (
                  <p style={{ marginTop: '10px', color: 'green' }}>{emailSentMessage}</p>
                )}
              </div>
            )}

          </div>
        )}
      </div>
    </>
  );
};

export default AirportTransferGroupPage;
```

---
## frontend/src/pages/AirportTransferPrivatePage.js

```js
// frontend/src/pages/AirportTransferPrivatePage.js
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import DatePicker from 'react-datepicker';
import TransferMap from '../components/TransferMap';
import PrivacyPolicyModal from '../components/PrivacyPolicyModal';
import 'react-datepicker/dist/react-datepicker.css';
import TransferContent from '../components/TransferContent';
import Breadcrumbs from "../components/Breadcrumbs";

// добавь после импортов:
const getIsoDate = (d) => {
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return local.toISOString().split('T')[0];
};

const textFromApi = (t, data) =>
  t(data?.message_key || data?.error_key || 'something_went_wrong');

const AirportTransferPrivatePage = () => {
  const { t, i18n } = useTranslation();

  const [hotel, setHotel] = useState('');
  const [hotelId, setHotelId] = useState(null);
  const [hotelSuggestions, setHotelSuggestions] = useState([]);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [date, setDate] = useState(null);
  const [pickupTime, setPickupTime] = useState('');
  const [pickupPoint, setPickupPoint] = useState('');
  const [pickupCoords, setPickupCoords] = useState(null);
  const [transfers, setTransfers] = useState([]);
  const [showInquiryForm, setShowInquiryForm] = useState(false);
  const [lastName, setLastName] = useState('');
  const [needLastName, setNeedLastName] = useState(false);
  const [email, setEmail] = useState('');
  const [checkboxAccepted, setCheckboxAccepted] = useState(false);
  const [emailSentMessage, setEmailSentMessage] = useState('');
  const [inquiryLastName, setInquiryLastName] = useState('');
  const [inquiryHotel, setInquiryHotel] = useState('');
  const [inquiryDate, setInquiryDate] = useState(null);
  const [inquiryFlight, setInquiryFlight] = useState('');
  const [inquiryMessage, setInquiryMessage] = useState('');
  const [inquiryEmail, setInquiryEmail] = useState('');
  const [inquirySuccessMessage, setInquirySuccessMessage] = useState('');
  const [inquiryHotelSuggestions, setInquiryHotelSuggestions] = useState([]);
  const [inquiryHotelId, setInquiryHotelId] = useState(null);
  const [inquirySuggestionsVisible, setInquirySuggestionsVisible] = useState(false);
  const [transferType] = useState('private');
  const [transferLoading, setTransferLoading] = useState(false);
  const [transferResult, setTransferResult] = useState(null);
  const [transferError, setTransferError] = useState('');
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [departureDate, setDepartureDate] = useState('');
  const [showPolicyModal, setShowPolicyModal] = useState(false);

  const [error, setError] = useState('');

  useEffect(() => {
    if (hotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${hotel}`)
        .then((res) => res.json())
        .then((data) => {
          setHotelSuggestions(data);
          setSuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей:', err));
    } else {
      setHotelSuggestions([]);
      setSuggestionsVisible(false);
    }
  }, [hotel]);

  const handleSelectHotel = (name, id) => {
    setHotel(name);
    setHotelId(id);
    setSelectedHotel({ id });
    setHotelSuggestions([]);
    setSuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!hotelId || !date) {
      setError(t('please_fill_all_fields'));
      return;
    }

    const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
    const dateStr = localDate.toISOString().split('T')[0];
    setDepartureDate(localDate);

    let url = `http://localhost:8000/api/transfer-schedule/?hotel_id=${hotelId}&date=${dateStr}&type=private`;
    if (lastName?.trim()) {
      url += `&last_name=${encodeURIComponent(lastName.trim())}`;
    }

    try {
      const response = await fetch(url);
      const data = await response.json();

      // ----- OK (200) -----
      if (response.ok) {
        // Успешный точный ответ
        if (data?.success === true) {
          setPickupTime(data.pickup_time || '');
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setNeedLastName(false);
          setShowInquiryForm(false);
          setError('');
          return;
        }

        // Нужна фамилия (несколько семей / нет фамилии)
        if (data?.success === false && data?.reason === 'need_last_name') {
          setNeedLastName(true);
          setPickupTime('');
          setPickupPoint('');
          setPickupCoords(null);
          setShowInquiryForm(false);
          setError(t('please_enter_last_name'));
          return;
        }

        // Время ещё не назначено — показываем понятное уведомление по ключу
        if (data?.success === false && data?.reason === 'time_pending') {
          setPickupTime(''); // времени нет
          setPickupPoint(data.pickup_point || '');
          setPickupCoords(
            data.pickup_lat && data.pickup_lng ? { lat: data.pickup_lat, lng: data.pickup_lng } : null
          );
          setNeedLastName(!!lastName); // если уже ввели фамилию — не просим снова
          setShowInquiryForm(false);
          setError(textFromApi(t, data)); // по message_key
          return;
        }

        // Есть подсказка по фамилии
        if (data?.success === false && data?.reason === 'no_exact_match' && data?.suggestion) {
          setError(`${t('did_you_mean')} "${data.suggestion}"?`);
          return;
        }

        // Не найдено конкретно по фамилии
        if (data?.success === false && data?.reason === 'not_found') {
          setError(t('no_transfer_for_lastname'));
          setShowInquiryForm(true);
          setPickupTime('');
          setPickupPoint('');
          setPickupCoords(null);
          return;
        }

        // fallback
        setError(textFromApi(t, data));
        return;
      }

      // ----- НЕ OK (404/400/…) -----
      // если бэк вернул ключ ошибки — показываем перевод
      if (data?.error_key || data?.message_key) {
        setError(textFromApi(t, data));
        // при «нет данных на дату/отель» показываем форму запроса
        if (data?.error_key === 'no_transfer_found' || data?.message_key === 'no_transfer_found') {
          setShowInquiryForm(true);
        }
      } else if (typeof data?.error === 'string' && data.error.toLowerCase().includes('no transfer')) {
        setError(t('no_transfer_found_message'));
        setShowInquiryForm(true);
      } else {
        setError(t('something_went_wrong'));
      }

      setPickupTime('');
      setPickupPoint('');
      setPickupCoords(null);
    } catch (err) {
      console.error(err);
      setError(t('something_went_wrong'));
    }
  };




  const handleInquirySubmit = async (e) => {
    e.preventDefault();

    if (!inquiryLastName || !inquiryHotelId || !inquiryDate || !inquiryEmail) {
      setError(t('please_fill_all_fields'));
      return;
    }

    try {
      const localDate = new Date(inquiryDate.getTime() - inquiryDate.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-inquiries/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          last_name: inquiryLastName.trim(),
          hotel: inquiryHotelId,
          departure_date: dateStr,
          flight_number: inquiryFlight.trim(),
          message: inquiryMessage.trim(),
          email: inquiryEmail.trim(),
          language: i18n.language, // ⬅️ ВАЖНО: добавляем текущий язык
        }),
      });

      if (response.ok) {
        setInquirySuccessMessage(t('request_sent_successfully'));

        setInquiryLastName('');
        setInquiryHotel('');
        setInquiryDate(null);
        setInquiryFlight('');
        setInquiryMessage('');
        setInquiryEmail('');
        setError('');
        setShowInquiryForm(false);
      } else {
        const data = await response.json();
        console.error('Ошибка запроса:', data);
        setError(t('request_error'));
      }
    } catch (err) {
      console.error('Ошибка соединения:', err);
      setError(t('request_error'));
    }
  };

  useEffect(() => {
    if (inquiryHotel.length >= 2) {
      fetch(`http://localhost:8000/api/hotels/?search=${inquiryHotel}`)
        .then((res) => res.json())
        .then((data) => {
          setInquiryHotelSuggestions(data);
          setInquirySuggestionsVisible(true);
        })
        .catch((err) => console.error('Ошибка загрузки отелей для запроса:', err));
    } else {
      setInquiryHotelSuggestions([]);
      setInquirySuggestionsVisible(false);
    }
  }, [inquiryHotel]);

  const handleSelectInquiryHotel = (name, id) => {
    setInquiryHotel(name);
    setInquiryHotelId(id);
    setInquiryHotelSuggestions([]);
    setInquirySuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0);
  };

  const handleFetchTransfer = async () => {
    setTransferLoading(true);
    setTransferResult(null);
    setTransferError('');

    if (!selectedHotel || !departureDate) {
      setTransferError(t('please_fill_all_fields'));
      setTransferLoading(false);
      return;
    }

    const params = new URLSearchParams({
      hotel_id: selectedHotel.id,
      date: departureDate.toISOString().split('T')[0],
      type: transferType,
    });

    if (lastName.trim() !== '') {
      params.append('last_name', lastName.trim());
    }

    try {
      const response = await fetch(`/api/transfer-schedule/?${params.toString()}`);
      const data = await response.json();

      if (!response.ok) {
        if (data.suggestion) {
          setTransferError(`${t('did_you_mean')}: ${data.suggestion}`);
        } else if (transferType === 'private' && !lastName) {
          setTransferError(t('please_enter_last_name'));
        } else {
          setTransferError(t('no_transfer_found_message'));
        }
      } else {
        setTransferResult(data);
      }
    } catch (error) {
      console.error("Ошибка при получении трансфера:", error);
      setTransferError(t('something_went_wrong'));
    }

    setTransferLoading(false);
  };


  const handleEmailSubmit = async () => {
    if (!email || !checkboxAccepted || !hotelId || !date) return;

    try {
      const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
      const dateStr = localDate.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/transfer-notifications/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email,
          hotel: hotelId,
          transfer_type: 'private',
          departure_date: dateStr,
          language: i18n.language,  // язык страницы
          last_name: lastName.trim()  // 🔹 это обязательно!
        })
      });

      if (response.ok) {
        setEmailSentMessage(t('email_sent_success'));
        setEmail('');
        setCheckboxAccepted(false);
      } else {
        const data = await response.json();
        console.error('Ошибка отправки:', data);
        setEmailSentMessage(t('email_send_error'));
      }
    } catch (err) {
      console.error(err);
      setEmailSentMessage(t('email_send_error'));
    }
  };

  const isValidEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);


  return (
    <>
      <PageBanner page="private_transfer" />
      

      
      <div className="page-container">

        <Breadcrumbs items={[
          { to: "/", label: t("home") },
          { to: "/airport-transfer", label: t("airport_transfer") },
          { label: t("private_transfer") } // или t("private_transfer")
        ]}/>
        
        <h1>{t('private_transfer')}</h1>
        <p>{t('enter_hotel_and_date')}</p>
        <TransferContent page="transfer_private" />
        
        <form onSubmit={handleSubmit} className="transfer-form left-aligned">
          <label>{t('enter_hotel')}</label>
          <div className="autocomplete-wrapper">
            <input
              type="text"
              value={hotel}
              onChange={(e) => setHotel(e.target.value)}
              placeholder={t('enter_hotel')}
              className="transfer-input"
            />
            {hotelSuggestions.length > 0 && !hotelSuggestions.some(h => h.name === hotel) && (
              <ul className="autocomplete-list">
                {hotelSuggestions.map((item) => (
                  <li key={item.id} onMouseDown={() => handleSelectHotel(item.name, item.id)}>
                    {item.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <label>{t('select_date')}</label>
          <DatePicker
            selected={date}
            onChange={(date) => setDate(date)}
            placeholderText={t('select_date')}
            className="transfer-input"
            dateFormat="yyyy-MM-dd"
          />

          <button
            type="submit"
            className="transfer-button"
            style={{ alignSelf: "flex-start" }}
          >
            {t('show_transfer_time')}
          </button>
        </form>

        {/* 🔹 Ошибка */}
        {error && (
          <div className="transfer-warning-box">
            {error}
          </div>
        )}

        {needLastName && (
          <div className="transfer-form left-aligned" style={{ marginTop: '20px' }}>
            <label htmlFor="lastNameInput">{t('enter_last_name')}</label>
            <input
              id="lastNameInput"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder={t('your_last_name')}
              className="transfer-input"
            />
            <button
              onClick={handleSubmit}
              className="transfer-button"
              style={{ marginTop: '15px' }}
            >
              {t('find_my_transfer')}
            </button>
          </div>
        )}

        

        {showInquiryForm && (
          <form
            onSubmit={handleInquirySubmit}
            className="transfer-form left-aligned inquiry-form-animated"
            style={{ marginTop: '20px' }}
          >
            <h3>{t('not_found_contact_us')}</h3>
            
            <label>{t('your_last_name')}</label>
            <input
              type="text"
              value={inquiryLastName}
              onChange={(e) => setInquiryLastName(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_hotel')}</label>
            <div className="autocomplete-wrapper">
              <input
                type="text"
                value={inquiryHotel}
                onChange={(e) => setInquiryHotel(e.target.value)}
                placeholder={t('your_hotel')}
                className="transfer-input"
              />
              {inquiryHotelSuggestions.length > 0 && !inquiryHotelSuggestions.some(h => h.name === inquiryHotel) && (
                <ul className="autocomplete-list">
                  {inquiryHotelSuggestions.map((item) => (
                    <li key={item.id} onMouseDown={() => handleSelectInquiryHotel(item.name, item.id)}>
                      {item.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>


            <label>{t('departure_date')}</label>
            <DatePicker
              selected={inquiryDate}
              onChange={(date) => setInquiryDate(date)}
              placeholderText={t('select_date')}
              className="transfer-input"
              dateFormat="yyyy-MM-dd"
            />

            <label>{t('flight_number')}</label>
            <input
              type="text"
              value={inquiryFlight}
              onChange={(e) => setInquiryFlight(e.target.value)}
              className="transfer-input"
            />

            <label>{t('question')}</label>
            <textarea
              value={inquiryMessage}
              onChange={(e) => setInquiryMessage(e.target.value)}
              className="transfer-input"
            />

            <label>{t('your_email')}</label>
            <input
              type="email"
              value={inquiryEmail}
              onChange={(e) => setInquiryEmail(e.target.value)}
              className="transfer-input"
            />

            <button className="transfer-button" style={{ marginTop: '15px' }}>
              {t('send_request')}
            </button>
          </form>
        )}

        {inquirySuccessMessage && !pickupTime && (
          <div className="success-message-box">
            {inquirySuccessMessage}
          </div>
        )}


        {pickupTime && (
          <div className="transfer-result">
            <h3>{t('pickup_time')}:</h3>
            <p>{pickupTime}</p>
            {pickupPoint && <p>{t('pickup_point')}: {pickupPoint}</p>}

            {pickupCoords && (
              <div style={{ height: '400px', marginTop: '20px' }}>
                <TransferMap lat={pickupCoords.lat} lng={pickupCoords.lng} pickupName={pickupPoint} />
              </div>
            )}

            {pickupTime && (
              <div className="email-subscription" style={{ marginTop: '30px' }}>
                <h3>{t('want_to_receive_email')}</h3>
                <p>{t('email_info_text')}</p>

                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('enter_email')}
                  className="transfer-input"
                  required
                />

                <div style={{ marginTop: '10px' }}>
                  <input
                    type="checkbox"
                    checked={checkboxAccepted}
                    onChange={(e) => setCheckboxAccepted(e.target.checked)}
                    id="consent"
                    onClick={(e) => e.stopPropagation()} // не даёт всплытию перейти к label
                  />
                  <label
                    htmlFor="consent"
                    style={{ marginLeft: '8px', cursor: 'pointer' }}
                    onClick={() => setShowPolicyModal(true)}
                  >
                    {t('i_agree_with')}{' '}
                    <span style={{ color: 'blue', textDecoration: 'underline' }}>
                      {t('terms_and_privacy')}
                    </span>
                  </label>
                </div>


                <PrivacyPolicyModal
                  isOpen={showPolicyModal}
                  onClose={() => setShowPolicyModal(false)}
                />

                <button
                  onClick={handleEmailSubmit}
                  className="transfer-button"
                  style={{
                    marginTop: '15px',
                    backgroundColor: (!checkboxAccepted || !isValidEmail(email)) ? '#ccc' : '#00aaff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    fontSize: '16px',
                    cursor: (!checkboxAccepted || !isValidEmail(email)) ? 'not-allowed' : 'pointer',
                    transition: '0.3s ease',
                  }}
                  disabled={!checkboxAccepted || !isValidEmail(email)}
                >
                  {t('send_to_email')}
                </button>


                {emailSentMessage && (
                  <p style={{ marginTop: '10px', color: 'green' }}>{emailSentMessage}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
};

export default AirportTransferPrivatePage;

```

---
## frontend/src/pages/AskQuestionPage.js

```js
// frontend/src/pages/AskQuestionPage.js
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css';
import { normalizeText } from '../helpers/normalizeText';

function AskQuestionPage() {
  const { t, i18n } = useTranslation();

  const [form, setForm] = useState({
    name: '',
    email: '',
    category: '',
    question: '',
  });
  const [status, setStatus] = useState(null);       // 'success' | 'error' | null
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const hasLettersOrNumbers = (s) =>
    Array.from(s).some((ch) => /\p{Letter}|\p{Number}/u.test(ch));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setStatus(null);
    setSubmitting(true);

    const payload = {
      name: normalizeText(form.name),
      email: normalizeText(form.email),
      category: form.category || 'other',
      language: i18n.language,
      question: normalizeText(form.question),   // 👈 единственное текстовое поле
      source: 'ask',
    };

    // клиентская проверка — не слать пустые/невидимые строки
    if (!hasLettersOrNumbers(payload.question)) {
      setStatus('error');
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/contact-questions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept-Language': i18n.language,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.message || 'send failed');

      setStatus('success');
      // очищаем только сообщение, имя/почту/категорию можно оставить
      setForm((prev) => ({ ...prev, question: '' }));
    } catch (err) {
      console.error('[AskQuestion] send error:', err);
      setStatus('error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageBanner page="ask" />

      <div className="page-container">
        <h2 style={{ textAlign: 'center', marginBottom: 20 }}>
          {t('ask_question')}
        </h2>
        <p className="welcome-text" style={{ textAlign: 'center' }}>
          {t('ask_intro')}
        </p>

        <form className="transfer-form left-aligned" onSubmit={onSubmit} noValidate>
          <label htmlFor="aq-name">{t('your_name')}</label>
          <input
            id="aq-name"
            type="text"
            name="name"
            value={form.name}
            onChange={onChange}
            className="transfer-input"
            autoComplete="name"
            required
          />

          <label htmlFor="aq-email">{t('your_email')}</label>
          <input
            id="aq-email"
            type="email"
            name="email"
            value={form.email}
            onChange={onChange}
            className="transfer-input"
            autoComplete="email"
            required
          />

          <label htmlFor="aq-category">{t('question_category')}</label>
          <select
            id="aq-category"
            name="category"
            value={form.category}
            onChange={onChange}
            className="transfer-input"
            required
          >
            <option value="">{t('select_category')}</option>
            <option value="transfer">{t('category_transfer')}</option>
            <option value="excursion">{t('category_excursion')}</option>
            <option value="organization">{t('category_organization')}</option>
            <option value="other">{t('category_other')}</option>
          </select>

          <label htmlFor="aq-question">{t('your_question')}</label>
          <textarea
            id="aq-question"
            name="question"             // 👈 важно: одно имя на всех языках
            rows="5"
            value={form.question}
            onChange={onChange}
            className="transfer-input"
            required
          />

          <button
            type="submit"
            className="transfer-button"
            style={{ marginTop: 20, alignSelf: 'flex-start' }}
            disabled={submitting}
          >
            {submitting ? (t('loading') || 'Sending...') : (t('send_question') || 'Send')}
          </button>
        </form>

        {status === 'success' && (
          <div className="success-message-box" style={{ marginTop: 12 }}>
            {t('success_message')}
          </div>
        )}
        {status === 'error' && (
          <div className="transfer-warning-box" style={{ marginTop: 12 }}>
            {t('error_message')}
          </div>
        )}
      </div>
    </>
  );
}

export default AskQuestionPage;

```

---
## frontend/src/pages/ContactsPage.js

```js
// frontend/src/pages/ContactsPage.js
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import '../styles/main.css';
import '../styles/contacts.css';
import { normalizeText } from '../helpers/normalizeText';

function ContactsPage() {
  const { t, i18n } = useTranslation();

  const [form, setForm] = useState({ name: '', email: '', question: '' });
  const [status, setStatus] = useState(null);        // 'success' | 'error' | null
  const [submitting, setSubmitting] = useState(false);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const hasLettersOrNumbers = (s) => Array.from(s).some((ch) => /\p{Letter}|\p{Number}/u.test(ch));

  const onSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;

    setStatus(null);
    setSubmitting(true);

    const payload = {
      name: normalizeText(form.name),
      email: normalizeText(form.email),
      language: i18n.language,
      question: normalizeText(form.question),   // 👈 единственное текстовое поле
      source: 'contacts',
      category: 'other',
    };

    // Клиентская проверка — чтобы не слать пустоту/невидимые символы
    if (!hasLettersOrNumbers(payload.question)) {
      setStatus('error');
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:8000/api/contact-questions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept-Language': i18n.language,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data?.message || 'send failed');

      // успех — чистим только сообщение, имя/почту можно оставить
      setStatus('success');
      setForm((prev) => ({ ...prev, question: '' }));
    } catch (err) {
      console.error('[Contacts] send error:', err);
      setStatus('error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <PageBanner page="contacts" />

      <div className="page-container">
        <h2 className="text-center mb-3">{t('contacts_title')}</h2>
        <p className="welcome-text text-center">{t('contacts_intro')}</p>

        {/* Кликовые карточки */}
        <div className="contacts-grid contacts-grid-compact">
          <a className="contact-card link-card" href="mailto:CostaSolinfo.Malaga@gmail.com">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5L4 8"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">{t('contacts_email')}</h3>
            </div>
          </a>

          <a className="contact-card link-card" href="https://wa.me/34660535089" target="_blank" rel="noreferrer">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M20 11.5A8.5 8.5 0 1 1 6.9 19L4 20l1-2.9A8.5 8.5 0 0 1 20 11.5Z"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">WhatsApp</h3>
            </div>
          </a>

          <a className="contact-card link-card" href="https://t.me/your_channel_or_username" target="_blank" rel="noreferrer">
            <div className="cc-header">
              <span className="cc-icon" aria-hidden>
                <svg viewBox="0 0 24 24">
                  <path d="M21 3 8.5 12.5M21 3l-7 18-2.5-8.5L3 10l18-7Z"
                        fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <h3 className="cc-title">{t('contacts_telegram')}</h3>
            </div>
          </a>
        </div>

        {/* Форма */}
        <div className="contact-form">
          <h3>{t('contacts_form_title')}</h3>

          <form onSubmit={onSubmit} className="contact-form-grid" noValidate>
            <div className="form-field">
              <label htmlFor="cf-name">{t('contacts_form_name')}</label>
              <input
                id="cf-name"
                type="text"
                name="name"
                value={form.name}
                onChange={onChange}
                className="transfer-input"
                autoComplete="name"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="cf-email">{t('contacts_form_email')}</label>
              <input
                id="cf-email"
                type="email"
                name="email"
                value={form.email}
                onChange={onChange}
                className="transfer-input"
                autoComplete="email"
                required
              />
            </div>

            <div className="form-field form-field--full">
              <label htmlFor="cf-message">{t('contacts_form_message')}</label>
              <textarea
                id="cf-message"
                name="question"           // 👈 важно: одно имя на всех языках
                value={form.question}
                onChange={onChange}
                rows="5"
                className="transfer-input"
                required
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="transfer-button" disabled={submitting}>
                {submitting ? (t('loading') || 'Sending...') : (t('contacts_form_send') || 'Send')}
              </button>
            </div>
          </form>

          {status === 'success' && (
            <div className="success-message-box" style={{ marginTop: 12 }}>
              {t('contacts_form_success')}
            </div>
          )}
          {status === 'error' && (
            <div className="transfer-warning-box" style={{ marginTop: 12 }}>
              {t('contacts_form_error')}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ContactsPage;

```

---
## frontend/src/pages/InfoMeetingPage.js

```js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTranslation } from 'react-i18next';
import PageBanner from '../components/PageBanner';
import Button from '../components/Button';

const InfoMeetingPage = () => {
  const { t, i18n } = useTranslation();
  const [welcomeText, setWelcomeText] = useState('');
  const [hotelQuery, setHotelQuery] = useState('');
  const [hotelOptions, setHotelOptions] = useState([]);
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [suggestionsVisible, setSuggestionsVisible] = useState(false);
  const [schedule, setSchedule] = useState([]);
  const [error, setError] = useState('');

  // 🔹 Загрузка текста страницы
  useEffect(() => {
    axios.get('/api/info-meeting/')
      .then(res => {
        const data = res.data;
        const localized = data[`content_${i18n.language}`] || data.content || '';
        setWelcomeText(localized);
      })
      .catch(() => setWelcomeText(''));
  }, [i18n.language]);

  // 🔹 Загрузка отелей по поиску
  useEffect(() => {
    if (hotelQuery.length < 2) {
      setHotelOptions([]);
      setSuggestionsVisible(false);
      return;
    }

    const timeout = setTimeout(() => {
      axios.get(`/api/hotels/?search=${hotelQuery}`)
        .then(res => {
          setHotelOptions(res.data);
          setSuggestionsVisible(true);
        })
        .catch(() => {
          setHotelOptions([]);
          setSuggestionsVisible(false);
        });
    }, 300);

    return () => clearTimeout(timeout);
  }, [hotelQuery]);

  // 🔹 Отправка запроса на расписание
  const handleSubmit = () => {
    if (!selectedHotel) return;

    axios.get(`/api/info-meetings/?hotel_id=${selectedHotel.id}`)
      .then(res => {
        const scheduleList = res.data.schedule;
        setSchedule(scheduleList);
        setError(scheduleList.length === 0 ? t('no_meetings_found') : '');
      })
      .catch(() => {
        setSchedule([]);
        setError(t('no_meetings_found'));
      });
  };

  // 🔹 Выбор отеля из подсказки
  const handleSelectHotel = (hotel) => {
    setSelectedHotel(hotel);
    setHotelQuery(hotel.name);
    setHotelOptions([]);
    setSuggestionsVisible(false);
    setTimeout(() => document.activeElement.blur(), 0); // снимаем фокус
  };

  return (
    <>
      <PageBanner page="info_meeting" />

      <div className="page-container">
        

        <div
          className="welcome-text"
          dangerouslySetInnerHTML={{ __html: welcomeText }}
        />

        <div className="info-meeting-form">
          <label htmlFor="hotelInput">{t('select_hotel')}</label>

          <div className="autocomplete-wrapper">
            <input
              id="hotelInput"
              className="transfer-input"
              type="text"
              value={hotelQuery}
              onChange={(e) => {
                setHotelQuery(e.target.value);
                setSelectedHotel(null);
              }}
              placeholder={t('choose_hotel')}
            />
            {suggestionsVisible && hotelOptions.length > 0 && !hotelOptions.some(h => h.name === hotelQuery) && (
              <ul className="autocomplete-list">
                {hotelOptions.map(hotel => (
                  <li key={hotel.id} onMouseDown={() => handleSelectHotel(hotel)}>
                    {hotel.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <Button onClick={handleSubmit} className="transfer-button">
              {t('check_schedule')}
            </Button>
          </div>
        </div>

        {schedule.length > 0 ? (
          <table className="schedule-table">
            <thead>
              <tr>
                <th>{t('date')}</th>
                <th>{t('time_from')}</th>
                <th>{t('time_to')}</th>
              </tr>
            </thead>
            <tbody>
              {schedule.map((item, index) => (
                <tr key={index}>
                  <td>{item.date}</td>
                  <td>{item.time_from}</td>
                  <td>{item.time_to}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : error && (
          <div className="error-message mt-4" style={{ textAlign: 'center', color: 'red' }}>
            {error}
          </div>
        )}
      </div>
    </>
  );
};

export default InfoMeetingPage;

```

---
## frontend/src/components/Navbar.js

```js
import React, { useState } from 'react';
import '../styles/navbar.css';
import logo from '../assets/logo_CostaSolinfo.PNG';
import { useTranslation } from 'react-i18next';
import { NavLink, Link } from 'react-router-dom';

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { t, i18n } = useTranslation();

  const toggleMenu = () => setIsOpen(!isOpen);
  const handleLanguageChange = (event) => i18n.changeLanguage(event.target.value);

  return (
    <nav className={`navbar ${isOpen ? 'active' : ''}`}>

      <div className="navbar-brand">
        <Link to="/" className="navbar-logo-link">
          <img src={logo} alt="CostaSolinfo" className="navbar-logo" />
        </Link>

        <div className="navbar-controls">
          <button className="burger" onClick={toggleMenu}>☰</button>
          <div className="lang-wrapper">
            <span className="lang-label">🌐</span>
            <select onChange={handleLanguageChange} value={i18n.language} className="lang-selector">
              <option value="ru">🇷🇺 Рус</option>
              <option value="en">🇬🇧 Eng</option>
              <option value="lt">🇱🇹 Lt</option>
              <option value="lv">🇱🇻 Lv</option>
              <option value="et">🇪🇪 Et</option>
              <option value="uk">🇺🇦 Ua</option>
              <option value="es">🇪🇸 Es</option>
            </select>
          </div>
        </div>
      </div>

      <div className={`navbar-links ${isOpen ? 'active' : ''}`}>
        <NavLink
          to="/"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('home')}
        </NavLink>

        <NavLink
          to="/excursions"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('excursions')}
        </NavLink>

        <NavLink
          to="/info-meeting"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('info_meeting')}
        </NavLink>

        <NavLink
          to="/airport-transfer"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('airport_transfer')}
        </NavLink>

        <NavLink
          to="/ask"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('ask')}
        </NavLink>

        <NavLink
          to="/contacts"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('contacts')}
        </NavLink>

        <NavLink
          to="/about"
          className={({ isActive }) => isActive ? 'active' : ''}
          onClick={() => setIsOpen(false)}
        >
          {t('about')}
        </NavLink>
      </div>

    </nav>
  );
}

export default Navbar;

```

---
## frontend/src/components/Footer.js

```js
import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/Footer.css";

const Footer = () => {
  const { t } = useTranslation();
  const year = new Date().getFullYear();

  // Заголовки/подписи с безопасным фолбэком
  const tagline = t("footer_tagline", "Ваш гид по Коста дель Соль");
  const navTitle = t("footer_nav_title", "Навигация");
  const contactsTitle = t("contacts");
  const rights = t("footer_rights", "Все права защищены.");

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Левая часть: логотип и слоган */}
        <div className="footer-left">
          <h2 className="footer-logo">CostaSolinfo</h2>
          <p className="footer-slogan">{tagline}</p>
        </div>

        {/* Средняя часть: ссылки */}
        <div className="footer-links">
          <h4>{navTitle}</h4>
          <ul>
            <li><Link to="/">{t("home")}</Link></li>
            <li><Link to="/excursions">{t("excursions")}</Link></li>
            <li><Link to="/info-meeting">{t("info_meeting")}</Link></li>
            <li><Link to="/airport-transfer">{t("airport_transfer")}</Link></li>
            <li><Link to="/ask">{t("ask")}</Link></li>
            <li><Link to="/contacts">{t("contacts")}</Link></li>
            <li><Link to="/about">{t("about")}</Link></li>
          </ul>
        </div>

        {/* Правая часть: контакты + соцсети */}
        <div className="footer-right contacts">{/* <-- добавлен класс contacts */}
          <h4>{contactsTitle}</h4>

          <p>
            Email{" "}
            <a href="mailto:CostaSolinfo.Malaga@gmail.com">
              CostaSolinfo.Malaga@gmail.com
            </a>
          </p>

          <p>
            WhatsApp{" "}
            <a href="https://wa.me/34660535089" target="_blank" rel="noreferrer">
              +34 660 535 089
            </a>
          </p>

          <div className="footer-socials">
            <a href="https://facebook.com" target="_blank" rel="noreferrer" aria-label="Facebook">
              <i className="fab fa-facebook"></i>
            </a>
            <a href="https://instagram.com" target="_blank" rel="noreferrer" aria-label="Instagram">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="https://wa.me/34660535089" target="_blank" rel="noreferrer" aria-label="WhatsApp">
              <i className="fab fa-whatsapp"></i>
            </a>
          </div>
        </div>
      </div>

      {/* Нижняя полоса */}
      <div className="footer-bottom">
        <div className="footer-bottom-left">
          <p>© {year} CostaSolinfo. {rights}</p>
        </div>

        <div className="footer-bottom-right">
          <button
            type="button"
            className="footer-linkbtn"
            onClick={() => window.csiOpenCookieSettings?.()}
            aria-label={t('cookies.settings', 'Cookie settings')}
            title={t('cookies.settings', 'Cookie settings')}
          >
            🍪 {t('cookies.settings', 'Cookie settings')}
          </button>

          <button
            type="button"
            className="footer-linkbtn"
            onClick={() => window.csiOpenPrivacy?.()}
            aria-label={t('privacy_policy', 'Privacy Policy')}
            title={t('privacy_policy', 'Privacy Policy')}
          >
            {t('privacy_policy')}
          </button>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

```

---
## frontend/src/components/PageBanner.js

```js
// PageBanner.js
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PageBanner.css';

function PageBanner({ page }) {
  const [banner, setBanner] = useState(null);
  const { i18n } = useTranslation();

  useEffect(() => {
    fetch(`http://localhost:8000/api/banner/${page}/`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.titles) {
          setBanner(data);
        } else {
          console.warn("Нет данных баннера или отсутствует titles:", data);
        }
      })
      .catch((error) => console.error("Ошибка загрузки баннера:", error));
  }, [page]);

  if (!banner) return null;

  const backgroundImage = `url(http://localhost:8000${banner.image})`;
  const title = banner.titles[i18n.language] || banner.titles.ru || '';

  return (
    <div className="page-banner-wrapper">
      <div className="page-banner" style={{ backgroundImage }}>
        <div className="page-banner-content">{title}</div>
      </div>
    </div>
  );
}

export default PageBanner;

```

---
## frontend/src/components/TransferMap.js

```js
// TransferMap.js
import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Настройка иконки маркера
const customIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

// Компонент перелёта карты к новой точке
const FlyToLocation = ({ lat, lng }) => {
  const map = useMap();

  useEffect(() => {
    if (lat && lng) {
      map.flyTo([lat, lng], 18, {
        duration: 1.5,
      });
    }
  }, [lat, lng]);

  return null;
};

const TransferMap = ({ lat, lng, pickupName }) => {
  if (!lat || !lng) return null;

  return (
    <div style={{ height: '400px', marginTop: '30px', borderRadius: '12px', overflow: 'hidden' }}>
      <MapContainer center={[lat, lng]} zoom={13} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
        />
        <Marker position={[lat, lng]} icon={customIcon}>
          <Popup>{pickupName || 'Точка сбора'}</Popup>
        </Marker>
        {/* Плавный перелет к новой точке */}
        <FlyToLocation lat={lat} lng={lng} />
      </MapContainer>
    </div>
  );
};

export default TransferMap;

```

---
## frontend/src/components/PickupMap.js

```js
import React, { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Исправляем баг с иконками Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// 🔹 Компонент для плавного перелёта карты
const FlyToLocation = ({ lat, lng }) => {
  const map = useMap();

  useEffect(() => {
    if (lat && lng) {
      map.flyTo([lat, lng], 15, {
        duration: 1.5,
      });
    }
  }, [lat, lng, map]);

  return null;
};

const PickupMap = ({ hotel, pickupPoint }) => {
  if (
    (!pickupPoint || pickupPoint.lat == null || pickupPoint.lng == null) &&
    (!hotel || hotel.lat == null || hotel.lng == null)
  ) {
    return <p style={{ textAlign: "center" }}>Нет данных для отображения карты</p>;
  }

  const center =
    pickupPoint?.lat && pickupPoint?.lng
      ? [pickupPoint.lat, pickupPoint.lng]
      : [hotel.lat, hotel.lng];

  return (
    <MapContainer
      center={center}
      zoom={15}
      style={{
        height: "400px",
        width: "100%",
        borderRadius: "10px",
        marginTop: "20px",
      }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
      />

      {hotel?.lat && hotel?.lng && (
        <Marker position={[hotel.lat, hotel.lng]}>
          <Popup>Ваш отель: {hotel.name}</Popup>
        </Marker>
      )}

      {pickupPoint?.lat && pickupPoint?.lng && (
        <Marker position={[pickupPoint.lat, pickupPoint.lng]}>
          <Popup>Точка сбора: {pickupPoint.name}</Popup>
        </Marker>
      )}

      {/* 🔹 Плавный перелёт */}
      <FlyToLocation lat={pickupPoint?.lat || hotel?.lat} lng={pickupPoint?.lng || hotel?.lng} />
    </MapContainer>
  );
};

export default PickupMap;

```

---
## frontend/src/components/PrivacyPolicyModal.js

```js
import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import '../styles/PrivacyPolicyModal.css';

const FOCUSABLE_SELECTORS =
  'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

const PrivacyPolicyModal = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const [policyText, setPolicyText] = useState('');
  const [loading, setLoading] = useState(true);

  const modalRef = useRef(null);               // контейнер модалки (для фокуса/ловушки)
  const previouslyFocusedRef = useRef(null);   // куда вернуть фокус после закрытия

  // Загрузка политики (с отменой на unmount/переключении языка)
  useEffect(() => {
    if (!isOpen) return;

    const controller = new AbortController();
    const fetchPolicy = async () => {
      try {
        setLoading(true);
        const res = await fetch(`/api/privacy-policy/?lang=${i18n.language}`, {
          headers: { 'Cache-Control': 'no-cache' },
          signal: controller.signal,
        });
        if (!res.ok || res.status === 204) throw new Error('Empty response');
        const data = await res.json();
        setPolicyText(data.content || t('policy_not_found'));
      } catch (err) {
        if (err.name !== 'AbortError') setPolicyText(t('error_loading_policy'));
      } finally {
        setLoading(false);
      }
    };

    fetchPolicy();
    return () => controller.abort();
  }, [isOpen, i18n.language, t]);

  // Блокировка скролла body + возврат фокуса после закрытия
  useEffect(() => {
    if (!isOpen) return;
    previouslyFocusedRef.current = document.activeElement;
    const { style } = document.body;
    const prevOverflow = style.overflow;
    style.overflow = 'hidden';

    return () => {
      style.overflow = prevOverflow;
      // Вернём фокус туда, где он был
      previouslyFocusedRef.current && previouslyFocusedRef.current.focus?.();
    };
  }, [isOpen]);

  // Фокус-ловушка + Escape
  useEffect(() => {
    if (!isOpen || !modalRef.current) return;

    const container = modalRef.current;
    const focusables = container.querySelectorAll(FOCUSABLE_SELECTORS);

    // Сфокусируем первый элемент внутри модалки (или сам контейнер)
    (focusables[0] || container).focus();

    const onKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose?.();
        return;
      }
      if (e.key !== 'Tab') return;

      const list = container.querySelectorAll(FOCUSABLE_SELECTORS);
      if (!list.length) return;

      const first = list[0];
      const last = list[list.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    container.addEventListener('keydown', onKeyDown);
    return () => container.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Закрытие по клику на затемнение
  const onOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose?.();
  };

  return (
    <div className="modal-overlay" onClick={onOverlayClick}>
      <div
        className="modal-content"
        role="dialog"
        aria-modal="true"
        aria-labelledby="policy-title"
        aria-describedby="policy-text"
        ref={modalRef}
        tabIndex={-1}
      >
        <h2 id="policy-title">{t('privacy_policy')}</h2>

        {loading ? (
          <p aria-busy="true">{t('loading')}...</p>
        ) : (
          <div
            id="policy-text"
            className="policy-text"
            // HTML берётся из админки (CKEditor); отрисовываем, как задумано
            dangerouslySetInnerHTML={{ __html: policyText }}
          />
        )}

        <button className="transfer-button" onClick={onClose}>
          {t('close')}
        </button>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal;

```

---
## frontend/src/components/Breadcrumbs.jsx

```js
import React from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "../styles/breadcrumbs.css";

/** items: [{ to?: string, label: string }] */
export default function Breadcrumbs({ items = [] }) {
  const last = items.length - 1;
  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <ol>
        {items.map((it, i) => (
          <li key={i} className={i === last ? "current" : ""}>
            {it.to && i !== last ? <Link to={it.to}>{it.label}</Link> : <span>{it.label}</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}

```

---
## frontend/src/helpers/normalizeText.js

```js
// helpers/normalizeText.js (один раз)
export const normalizeText = (val) => {
  if (val == null) return '';
  let s = String(val);
  s = s.normalize('NFKC');
  s = s.replace(/\u00A0/g, ' ');
  s = s.replace(/[\u200B\u200C\u200D\uFEFF]/g, '');
  s = s.replace(/^\s+|\s+$/g, '');
  s = s.replace(/\s+/g, ' ');
  return s;
};

```

---
## frontend/src/hooks/usePageContent.js

```js
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

export const usePageContent = (endpoint) => {
  const [data, setData] = useState(null);
  const { i18n } = useTranslation();

  useEffect(() => {
    fetch(`/api/${endpoint}/`, {
      headers: { 'Accept-Language': i18n.language }
    })
      .then(res => res.json())
      .then(json => setData(json))
      .catch(err => console.error(err));
  }, [endpoint, i18n.language]);

  return data;
};

```

---
## frontend/src/styles/main.css

```css
:root{
  --csi-primary:#0057A3;
  --csi-primary-600:#004a8b;
  --csi-accent:#ffc400;
  --csi-ink:#1f2937;
  --csi-muted:#6b7280;
}

/* ========== ГЛОБАЛЬНЫЕ СТИЛИ ========== */
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #fff;
  color: #222;
}

/* ========== Общая обёртка ========== */
.app-wrapper {
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background-color: #fff;
  color: #222;
}

/* ========== Контент страницы ========== */
.page {
  padding: 10px 0;
}



/* Стили кнопок трансферов */
.transfer-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.transfer-button {
  background-color: #0071c2 !important;
  color: white;
  font-weight: bold;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  min-width: 300px;         /* 🔹 фиксированная ширина */
  text-align: center;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.transfer-button:hover {
  background-color: #005b9a !important;
}

/* Форма группового трансфера */
.transfer-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
  margin-top: 30px;
}

.transfer-form label {
  font-weight: bold;
  margin-top: 15px;
}

.transfer-form.left-aligned {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 500px;
  min-width: 400px;         /* 🔹 чтобы форма не сжималась */
  margin-top: 30px;
}

.transfer-input {
  width: 300px;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #ccc;
  box-sizing: border-box;
  transition: border 0.2s ease, box-shadow 0.2s ease;
}

.transfer-input:focus {
  outline: none;
  border: 2px solid #007BFF; /* Ярко-синий */
  box-shadow: 0 0 6px rgba(0, 123, 255, 0.5);
}

.transfer-result {
  text-align: center;
  margin-top: 30px;
  font-size: 18px;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 20px;
}

.autocomplete-wrapper {
  position: relative;
  max-width: 400px;
}

.autocomplete-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 10;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  list-style: none;
  padding: 0;
  margin: 5px 0 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
}

.autocomplete-list li {
  padding: 10px;
  cursor: pointer;
}

.autocomplete-list li:hover {
  background-color: #f0f0f0;
}

/* Стили предупреждения что трансфер не найден */
.transfer-warning-box {
  border: 2px solid #ff4d4f;
  background-color: #fff1f0;
  color: #cf1322;
  padding: 15px;
  border-radius: 8px;
  font-weight: bold;
  max-width: 600px;
  margin: 20px auto;
  text-align: center;
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Стиль об успешной отправке запроса по трансферу */
.success-message-box {
  border: 2px solid #4CAF50;         /* Зелёная рамка */
  background-color: #eafaf1;         /* Светлый фон */
  color: #2e7d32;                    /* Зелёный текст */
  padding: 15px;
  margin-top: 20px;
  border-radius: 8px;
  font-size: 16px;
  text-align: center;
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Анимация открытия формы */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.inquiry-form-animated {
  animation: fadeIn 0.4s ease-in-out;
}

.info-meeting-form {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 500px;
  min-width: 300px;
  margin: 0 auto;
}

.info-meeting-form label {
  font-weight: bold;
  margin-bottom: 8px;
}

.info-meeting-select {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #ccc;
  margin-bottom: 20px;
}

.welcome-text {
  font-size: 16px;
  color: #444;
  line-height: 1.6;
  margin-bottom: 20px;
}

/* Добавь в твой CSS-файл (например, InfoMeetingPage.css или глобально) */

.schedule-table {
  width: 100%;
  max-width: 600px;
  margin: 30px auto;
  border-collapse: collapse;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.schedule-table thead {
  background-color: #f7f7f7;
  font-weight: bold;
}

.schedule-table th,
.schedule-table td {
  border: 1px solid #ddd;
  padding: 12px;
  text-align: center;
}

.schedule-table tbody tr:nth-child(even) {
  background-color: #f9f9f9;
}

@media (max-width: 500px) {
  .schedule-table th,
  .schedule-table td {
    font-size: 14px;
    padding: 8px;
  }
}


/* ==== АДАПТИВНЫЕ ОВЕРРАЙДЫ ==== */

/* 0) Единая анимация (оставь только один fadeIn в файле) */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 1) Кнопки выбора типа трансфера — флюидные + фирменный синий */
.transfer-buttons {
  gap: clamp(12px, 3vw, 20px);
}

.transfer-button {
  /* цвет в стиле CostaSolinfo */
  background-color: #0057A3 !important;
  transition: background-color .25s ease, transform .05s ease;
  padding: clamp(10px, 2.8vw, 12px) clamp(16px, 4.2vw, 24px);
  font-size: clamp(14px, 1.8vw, 16px);
  min-width: unset;        /* снимаем жёсткую ширину */
  width: min(100%, 360px); /* аккуратная ширина на мобилках */
}

.transfer-button:hover { background-color: #004a8b !important; }
.transfer-button:active { transform: translateY(1px); }

/* 2) Формы трансферов — без жёстких min-width */
.transfer-form { gap: clamp(10px, 2.2vw, 15px); }

.transfer-form.left-aligned {
  align-items: stretch;
  max-width: 560px;
  min-width: 0;            /* <— убираем блокирующее сжатие */
  width: 100%;
  margin-top: 24px;
}

/* Поля ввода — флюидные */
.transfer-input,
.info-meeting-select {
  width: 100%;
  max-width: 420px;        /* ограничитель на десктопе */
  padding: clamp(10px, 2.5vw, 12px);
  font-size: clamp(14px, 1.8vw, 16px);
}

/* 3) Автокомплит — растягиваем и улучшаем тач‑таргеты */
.autocomplete-wrapper {
  width: 100%;
  max-width: 560px;        /* как форма */
}

.autocomplete-list {
  width: 100%;
  z-index: 1000;           /* поверх прочего UI */
  max-height: 240px;
}

.autocomplete-list li {
  padding: clamp(10px, 2.6vw, 14px);
}

/* 4) Боксы предупреждений/успеха — флюидные */
.transfer-warning-box,
.success-message-box {
  width: 100%;
  max-width: 720px;
  margin: 16px auto;
  font-size: clamp(14px, 2vw, 16px);
}

/* 5) Info‑meeting форма — флюидная */
.info-meeting-form {
  align-items: stretch;
  max-width: 560px;
  min-width: 0;
  width: 100%;
  padding-inline: 0;
}

/* 6) Таблица расписаний — безопасный скролл на узких экранах */
.schedule-table {
  width: 100%;
  margin: 24px auto;
  font-size: clamp(14px, 2vw, 16px);
}

@media (max-width: 600px) {
  /* кладём таблицу в горизонтальный скролл, чтобы ничего не ломать разметкой */
  .schedule-table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
  }
  .schedule-table thead,
  .schedule-table tbody,
  .schedule-table tr,
  .schedule-table th,
  .schedule-table td {
    white-space: nowrap;
  }
}

/* 7) Общие мобильные улучшения */
@media (max-width: 768px) {
  .transfer-buttons { justify-content: center; }
  .transfer-result { font-size: 16px; }
  .welcome-text { font-size: 15px; }
}

@media (max-width: 480px) {
  .page { padding: 6px 0; }
  .transfer-button { width: 100%; }  /* полноразмерная кнопка */
  .transfer-form { margin-top: 20px; }
  .transfer-form.left-aligned { margin-top: 20px; }
}


@media print {
  nav, .navbar, .footer, .page-banner, .cookie-banner, .csi-cookie-overlay { display:none !important; }
  .main-container, .page-container { padding:0 !important; box-shadow:none !important; }
  a[href]:after{ content:" (" attr(href) ")"; font-size:0.85em; color:#555; }
}

```

---
## frontend/src/styles/ExcursionsPage.css

```css
/* src/styles/ExcursionsPage.css */

.excursions-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: clamp(14px, 3.5vw, 20px);
}

/* Сетка карточек */
.excursions-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); /* авто‑подбор колонок */
  gap: clamp(14px, 2.8vw, 20px);
  margin-top: clamp(14px, 3vw, 20px);
}

/* Карточка экскурсии */
.excursion-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 8px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  text-align: left;
  padding: clamp(12px, 2.8vw, 16px);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}

/* hover только там, где он есть */
@media (hover: hover) {
  .excursion-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 18px rgba(0,0,0,0.14);
    border-color: rgba(0,0,0,0.12);
  }
}

/* Изображение */
.excursion-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;              /* вместо фикс. 180px */
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.04);
}

/* Заголовок */
.excursion-card h2 {
  font-size: clamp(16px, 2.3vw, 18px);
  margin: 10px 0 6px;
  color: #222;
  line-height: 1.3;
}

/* Короткое описание в карточке (обрезка до 3 строк) */
.excursion-intro,
.excursion-description {
  font-size: clamp(14px, 2vw, 15px);
  color: #555;
  line-height: 1.5;
  margin: 8px 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Кнопка */
.excursion-card a {
  display: inline-block;
  align-self: flex-start;            /* к левой кромке */
  padding: 8px 14px;
  background: #0057A3;               /* фирменный синий */
  color: #fff;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.92rem;
  transition: background .2s ease, transform .05s ease;
}
.excursion-card a:hover { background: #004a8b; }
.excursion-card a:active { transform: translateY(1px); }
.excursion-card a:focus-visible { outline: 2px solid #0057A3; outline-offset: 2px; }

/* Подвал карточки (если используешь блок с ценой/днями) */
.excursion-card p {
  font-size: clamp(13px, 1.8vw, 14px);
  color: #666;
  margin: 6px 0 10px;
}

/* Адаптивные уточнения */
@media (max-width: 900px) {
  /* сетка сама схлопнется в 2 колонки по minmax; ничего делать не надо */
}

@media (max-width: 600px) {
  .excursions-container { padding: 12px; }
  .excursion-card { border-radius: 10px; }
}

/* Уважение настроек пользователя */
@media (prefers-reduced-motion: reduce) {
  .excursion-card, .excursion-card a { transition: none; }
}

```

---
## frontend/src/styles/ExcursionDetailPage.css

```css
/* ===== Контейнер и базовая типографика ===== */
.excursion-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: clamp(14px, 3.5vw, 20px);
  text-align: left;
}

.excursion-description {
  font-size: clamp(15px, 1.9vw, 16px);
  line-height: 1.65;
  margin: clamp(14px, 3vw, 20px) 0;
}

.excursion-block { margin-bottom: clamp(14px, 3vw, 20px); }

/* ===== Галерея (лента с прокруткой) ===== */
.excursion-gallery-container { position: relative; }

.excursion-gallery {
  display: flex;
  overflow-x: auto;
  gap: clamp(10px, 2.5vw, 15px);
  padding: 10px;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}
.excursion-gallery::-webkit-scrollbar { height: 8px; }
.excursion-gallery::-webkit-scrollbar-thumb { background: rgba(0,0,0,.18); border-radius: 4px; }

.excursion-gallery img {
  flex: 0 0 auto;
  width: clamp(220px, 48vw, 280px);
  height: clamp(150px, 32vw, 200px);
  object-fit: cover;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  transition: transform .25s ease;
}

@media (hover: hover) {
  .excursion-gallery img:hover { transform: scale(1.05); }
}

/* ===== Стрелки галереи ===== */
.gallery-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: clamp(28px, 4.2vw, 40px);
  color: #333;
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(0,0,0,.08);
  border-radius: 12px;
  cursor: pointer;
  z-index: 2;
  transition: transform .2s ease, color .2s ease, background .2s ease;
  padding: 6px 10px;
  line-height: 1;
}
@media (hover: hover) {
  .gallery-arrow:hover {
    color: #0057A3;
    transform: translateY(-50%) scale(1.06);
    background: rgba(255,255,255,0.95);
  }
}
.gallery-arrow.left  { left: -28px; }
.gallery-arrow.right { right: -28px; }

@media (max-width: 768px) {
  /* На мобилках делаем стрелки внутри контейнера и скрываем по умолчанию */
  .gallery-arrow { opacity: 0; pointer-events: none; left: 6px; right: 6px; }
  .gallery-arrow.left { left: 6px; }
  .gallery-arrow.right { right: 6px; }
  .gallery-container.show-arrows .gallery-arrow { opacity: 1; pointer-events: auto; }
}

/* ===== Модальное окно (fullscreen) ===== */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: grid;
  place-items: center;
  z-index: 11000; /* выше cookie/прочих оверлеев */
}
.modal img {
  max-width: min(92vw, 1200px);
  max-height: 82vh;
  border-radius: 10px;
  box-shadow: 0 24px 60px rgba(0,0,0,.35);
}

.modal .close-btn {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 2rem;
  color: #fff;
  cursor: pointer;
  background: transparent;
  border: 0;
  line-height: 1;
}

.modal .modal-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: clamp(34px, 5vw, 48px);
  color: #fff;
  cursor: pointer;
  background: rgba(0,0,0,.25);
  border-radius: 12px;
  padding: 6px 10px;
}
.modal .modal-arrow.left  { left: 10px; }
.modal .modal-arrow.right { right: 10px; }

@media (prefers-reduced-motion: reduce) {
  .excursion-gallery img,
  .gallery-arrow { transition: none; }
}

/* ===== Блок выбора отеля/кнопки ===== */
.hotel-select { margin: 20px 0; }

.book-button {
  background-color: #0057A3;
  color: #fff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: background-color .2s ease, transform .05s ease;
}
.book-button:hover { background-color: #004a8b; }
.book-button:active { transform: translateY(1px); }

/* подпись к инпуту */
.hotel-label {
  display: block;
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 8px;
  color: #333;
}

/* автокомплит отелей */
.hotel-select {
  margin: 20px 0;
  position: relative;
  max-width: min(100%, 480px);
}
.hotel-select input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}
.hotel-select ul {
  list-style: none;
  padding: 0;
  margin: 6px 0 0;
  border: 1px solid #ccc;
  border-radius: 8px;
  max-height: 240px;
  overflow-y: auto;
  position: absolute;
  inset-inline: 0;
  background: #fff;
  z-index: 12000; /* поверх карты и контента */
  box-shadow: 0 8px 22px rgba(0,0,0,.1);
}
.hotel-select li {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}
.hotel-select li:hover { background-color: #f5f7fa; }

/* ===== Кнопка Google Maps и блоки информации ===== */
.google-maps-button-container {
  margin-top: 15px;
  text-align: left;
  position: relative;
  z-index: 10;
}

.pickup-section { margin-top: 25px; }

.pickup-details {
  margin-bottom: 10px;
  text-align: left;
  font-size: clamp(16px, 2vw, 18px);
}
.pickup-time {
  font-weight: 700;
  font-size: clamp(18px, 2.4vw, 20px);
  color: #d93025; /* заметный красный, менее «ядовитый» чем чистый red */
  margin-bottom: 8px;
}

/* ===== Цены / пометки ===== */
.excursion-prices { font-size: clamp(16px, 2vw, 18px); }
.excursion-prices .price-adult {
  font-weight: 700;
  color: #0057A3;
  margin: 5px 0;
}
.excursion-prices .price-child {
  font-weight: 700;
  color: #ff9800;
  margin: 5px 0;
}
.child-note {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

/* ===== Секция выбора отеля (блок) ===== */
.hotel-select-block {
  background: #f0f8ff;
  padding: clamp(18px, 4vw, 25px);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin: clamp(20px, 5vw, 40px) auto;
  max-width: 700px;
  text-align: center;
}
.hotel-title {
  font-size: clamp(18px, 2.6vw, 22px);
  font-weight: 700;
  color: #0057A3;
  margin-bottom: 10px;
}
.hotel-instruction {
  font-size: clamp(14px, 2.2vw, 16px);
  color: #333;
  margin-bottom: 14px;
}

/* Поле отеля (id=hotel-input) — подчистим палитру под бренд */
#hotel-input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #0057A3;
  border-radius: 8px;
  box-sizing: border-box;
  transition: box-shadow .2s, border-color .2s;
}
#hotel-input:focus {
  border-color: #28a745; /* зелёный акцент при фокусе допустим */
  box-shadow: 0 0 10px rgba(40,167,69,0.25);
  outline: none;
}

/* ===== Мелкие уточнения для мобильных ===== */
@media (max-width: 600px) {
  .pickup-title {
    font-size: 20px;
    margin: 12px 0;
  }
  .google-maps-button-container { text-align: center; }
  .hotel-select { max-width: 100%; }
}

```

---
## frontend/src/styles/Footer.css

```css
.footer {
  background: #f9f9f9;
  border-top: 1px solid #ddd;
  padding: 30px 20px 10px;
  font-family: Arial, sans-serif;
  color: #333;
}

.footer-container {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  max-width: 1200px;
  margin: 0 auto;
}

.footer-left,
.footer-links,
.footer-right {
  flex: 1;
  min-width: 220px;
  margin: 10px;
}

.footer-logo {
  color: #0057A3;
  font-size: 22px;
  font-weight: bold;
  margin-bottom: 5px;
}

.footer-slogan {
  color: #666;
  font-size: 14px;
}

.footer-links h4,
.footer-right h4 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #0057A3;
}

.footer-links ul {
  list-style: none;
  color: #0057A3;
  padding: 0;
}

.footer-links ul li {
  margin: 6px 0;
  color: #0057A3;
}

.footer-links ul li a {
  text-decoration: none;
  color: #333;
  transition: color 0.3s;
}

.footer-links ul li a:hover {
  color: #007bff;
}

.footer-right p {
  margin: 6px 0;
  font-size: 14px;
}

.footer-socials {
  margin-top: 15px;
}

.footer-socials a {
  margin-right: 15px;
  font-size: 20px;
  color: #333;
  transition: color 0.3s;
}

.footer-socials a:hover {
  color: #007bff;
}

:root{
  --csi-primary:#007aff;     /* ваш синий */
  --csi-accent:#ffc400;      /* ваш жёлтый */
  --csi-ink:#1f2937;
  --csi-muted:#6b7280;
}

/* нижняя полоса футера — в две колонки */
.footer-bottom{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:12px;
  padding:10px 0 0;
  border-top:1px solid #e5e7eb;
  margin-top:14px;
  flex-wrap:wrap;
}
.footer-bottom-left p{
  margin:0;
  color:var(--csi-muted);
  font-size:14px;
}
.footer-bottom-right{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
}

/* тихая ссылко-кнопка */
.footer-linkbtn {
  border: 0;
  background: transparent;
  padding: 6px 8px;
  color: #0057A3;              /* фирменный синий */
  font-size: 14px;
  line-height: 1;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease, background 0.2s ease;
}

.footer-linkbtn:hover {
  background: rgba(0, 122, 255, 0.08);   /* лёгкий синий фон при ховере */
}

.footer-linkbtn:focus {
  outline: 2px solid #007aff;
  outline-offset: 2px;
}


.footer .contacts a {
  color: #333;              /* обычный цвет текста */
  text-decoration: none;    /* убираем подчёркивание */
  font-weight: 400;         /* делаем одинаковый вес с текстом */
}

.footer .contacts a:hover {
  color: #0057A3;           /* 👈 при наведении фирменный синий */
  text-decoration: underline; /* можно вернуть подчёркивание */
}

/* =========================
   АДАПТИВ — планшеты (< 992px)
   ========================= */
@media (max-width: 992px) {
  .footer-container {
    gap: 8px;
  }

  .footer-left,
  .footer-links,
  .footer-right {
    min-width: 260px;     /* карточки пошире */
    flex: 1 1 45%;        /* две колонки */
  }

  .footer-links h4,
  .footer-right h4 {
    margin-bottom: 8px;
  }

  .footer-bottom {
    padding-top: 12px;
  }
}

/* =========================
   АДАПТИВ — мобильные (< 600px)
   ========================= */
@media (max-width: 600px) {
  .footer {
    padding: 22px 16px 8px;
  }

  /* колонки в столбик + выравнивание по центру */
  .footer-container {
    flex-direction: column;
    align-items: center;
  }

  .footer-left,
  .footer-links,
  .footer-right {
    margin: 6px 0;
    min-width: 100%;
    text-align: center;
  }

  /* список ссылок — в две колонки, если помещается */
  .footer-links ul {
    display: grid;
    grid-template-columns: repeat(2, minmax(120px, 1fr));
    gap: 6px 16px;
    justify-items: center;
  }

  /* соцсети — центр и крупнее тач-таргеты */
  .footer-socials {
    margin-top: 10px;
    display: flex;
    justify-content: center;
    gap: 14px;
  }
  .footer-socials a {
    font-size: 22px;
  }

  /* нижняя полоса — в столбик, по центру */
  .footer-bottom {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  .footer-bottom-left p {
    font-size: 13px;
  }
  .footer-bottom-right {
    justify-content: center;
  }

  /* «тихие» кнопки — чуть крупнее тач-таргеты */
  .footer-linkbtn {
    padding: 8px 10px;
    border-radius: 10px;
  }
}

/* =========================
   МЕЛКИЕ ЭКРАНЫ (< 360px)
   ========================= */
@media (max-width: 360px) {
  .footer-links ul {
    grid-template-columns: 1fr; /* по одной ссылке в строке */
    gap: 6px;
  }
}


```

---
## frontend/src/styles/breadcrumbs.css

```css
/* ===== Breadcrumbs (контрастная версия) ===== */
.breadcrumbs {
  margin: clamp(6px, 2vw, 16px) 0;
  font-size: clamp(14px, 1.4vw, 15px);   /* чуть крупнее */
  letter-spacing: .2px;
  color: #374151;                         /* slate-700 */
}

.breadcrumbs ol {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: clamp(6px, 1.6vw, 10px);
  flex-wrap: wrap;
}

.breadcrumbs li {
  display: inline-flex;
  align-items: center;
  /* убираем общую полупрозрачность */
  opacity: 1;
  white-space: nowrap;
  max-width: 50vw;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #6b7280;                         /* slate-500 — для «обычных» элементов */
  font-weight: 500;
}

.breadcrumbs li.current {
  color: #111827;                         /* slate-900 — активный */
  font-weight: 600;
}

/* разделитель — явный цвет, без opacity */
.breadcrumbs li:not(.current)::after {
  content: "›";
  margin: 0 clamp(4px, 1vw, 8px);
  color: #9ca3af;                         /* slate-400 */
}

/* ссылки — явный цвет + hover */
.breadcrumbs a {
  color: #374151;                         /* совпадает с .breadcrumbs */
  text-decoration: none;
  border-bottom: 1px dotted transparent;
  transition: border-color .2s ease, color .2s ease;
}
.breadcrumbs a:hover {
  color: #0ea5e9;                         /* sky-500 */
  border-bottom-color: currentColor;
}

/* видимый фокус */
.breadcrumbs a:focus-visible {
  outline: 2px solid #0ea5e9;
  outline-offset: 2px;
  border-bottom-color: transparent;
}

/* RTL */
:root:dir(rtl) .breadcrumbs li:not(.current)::after { content: "‹"; }

/* тёмная тема (если понадобится) */
@media (prefers-color-scheme: dark) {
  .breadcrumbs { color: #e5e7eb; }
  .breadcrumbs li { color: #d1d5db; }
  .breadcrumbs li.current { color: #fff; }
  .breadcrumbs li:not(.current)::after { color: #9ca3af; }
  .breadcrumbs a:hover { color: #93c5fd; }
}

```

---
## frontend/src/pages/HomePage.css

```css
/* ===== Home page ===== */

/* Контейнер главной (работает и для .page-container, и для .home-page) */
.page-container,
.home-page {
  padding: clamp(14px, 3.5vw, 20px);
  max-width: 1000px;  /* как у баннера */
  margin: 0 auto;
}

/* Баннер */
.homepage-banner {
  width: 100%;
  max-width: 1000px;
  height: auto;
  display: block;
  border-radius: 12px;
  margin-bottom: clamp(14px, 3.5vw, 20px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, .1);
}

/* Заголовок */
.homepage-title {
  font-size: clamp(20px, 5vw, 32px);
  font-weight: 800;
  margin-bottom: 10px;
  line-height: 1.2;
  color: #0f172a;
}

/* Подзаголовок / контент из админки */
.homepage-subtitle {
  font-size: clamp(15px, 2.2vw, 17px);
  line-height: 1.7;
  color: #333;
  white-space: normal;       /* важно: не 'pre-line' */
  width: 100%;
  max-width: 1000px;         /* = ширина баннера */
  margin: 0 auto;
  text-align: left;          /* читается лучше, чем общий justify */
}

/* Аккуратные отступы внутри контента */
.homepage-subtitle h2,
.homepage-subtitle h3 { margin: 0.6em 0 0.4em; }
.homepage-subtitle p { margin: 0.5em 0; }
.homepage-subtitle ul,
.homepage-subtitle ol { margin: 0.4em 0 0.8em 1.2em; }
.homepage-subtitle li { margin: 0.3em 0; }
.homepage-subtitle strong { font-weight: 700; }
.homepage-subtitle em { font-style: italic; }

/* Мобильные мелочи */
@media (max-width: 600px) {
  .homepage-banner {
    border-radius: 10px;
    box-shadow: 0 3px 12px rgba(0,0,0,.08);
  }
}

```

---
## frontend/src/locales/ru/translation.json

```json
{
  "home": "Главная",
  "excursions": "Экскурсии",
  "info_meeting": "Инфо встреча",
  "airport_transfer": "Трансфер в аэропорт",
  "ask": "Задать вопрос",
  "contacts": "Контакты",
  "about": "О нас",
  "transfer_to_airport": "Выберите тип Вашего трансфер",
  "group_transfer": "Групповой трансфер",
  "private_transfer": "Индивидуальный трансфер",
  "please_enter_last_name": "Пожалуйста, введите Вашу фамилию",
  "enter_hotel_and_date": "Укажите отель и дату вылета, чтобы получить точное время трансфера",
  "enter_hotel": "Введите название отеля",
  "select_date": "Выберите дату трансфера",
  "show_transfer_time": "Показать время трансфера",
  "pickup_time": "Время трансфера",
  "pickup_point": "Точка отправления",
  "please_fill_all_fields": "Пожалуйста, заполните все поля",
  "something_went_wrong": "Произошла ошибка. Попробуйте снова.",
  "want_to_receive_email": "Хотите получить эту информацию на почту?",
  "email_info_text": "Мы отправим вам время трансфера и ссылку на карту. Если произойдут изменения — вы получите новое письмо.",
  "enter_email": "Введите ваш email",
  "consent_text": "Я ознакомлен с правилами и политикой конфиденциальности",
  "footer_tagline": "Ваш гид по Коста дель Соль",
  "footer_nav_title": "Навигация",
  "footer_rights": "Все права защищены.",
  "send_to_email": "Отправить на почту",
  "email_sent_success": "Информация успешно отправлена на вашу почту!",
  "email_send_error": "Ошибка при отправке письма. Попробуйте позже.",
  "enter_last_name": "Фамилия",
  "your_last_name": "Введите фамилию",
  "find_my_transfer": "Уточнить трансфер",
  "no_transfer_found": "На выбранную дату или отель нет данных по трансферу.",
  "did_you_mean": "Возможно, вы имели в виду",
  "not_found_contact_us": "Если вы не нашли свой трансфер — свяжитесь с представителем через форму связи ниже:",
  "open_contact_form": "Открыть форму для запроса",
  "your_hotel": "Отель проживания",
  "departure_date": "Дата вылета",
  "flight_number": "Номер рейса (если есть)",
  "question": "Ваш вопрос",
  "your_email": "Электронная почта",
  "send_request": "Отправить запрос",
  "request_sent_successfully": "Ваш запрос успешно отправлен. Мы проверим информацию и свяжемся с вами по электронной почте.",
  "request_error": "Произошла ошибка при отправке запроса.",
  "no_transfer_schedule_for_this_date": "На выбранную дату или отель нет трансфера. Вы можете отправить запрос ниже.",
  "no_transfer_for_lastname": "По указанной фамилии трансфер не найден. Вы можете уточнить информацию через форму.",
  "no_transfer_found_message": "На выбранную дату или отель нет данных по трансферу. Вы можете отправить запрос ниже для уточнения данных.",
  "enter_your_email_label": "Введите Вашу почту",
  "enter_your_lastname_label": "Укажите Вашу фамилию",
  "i_agree_with": "Я ознакомлен с",
  "terms_and_privacy": "правилами и политикой конфиденциальности",
  "privacy_policy": "Политика конфиденциальности",
  "privacy_policy_text": "Политика конфиденциальности будет добавлена позже. Здесь будет текст, описывающий как мы храним и обрабатываем ваши данные.",
  "close": "Закрыть",
  "loading": "Загрузка",
  "policy_not_found": "Политика не найдена",
  "error_loading_policy": "Ошибка при загрузке политики",
  "info_meeting_title": "Инфо встреча",
  "select_hotel": "Выберите ваш отель:",
  "choose_hotel_placeholder": "Начните вводить название отеля",
  "check_schedule": "Узнать расписание",
  "date": "Дата",
  "time_from": "От",
  "time_to": "До",
  "no_meetings_found": "Для выбранного отеля встречи пока не запланированы.",
  "no_excursions_found": "Экскурсии не найдены",
  "duration": "Продолжительность",
  "hours": "ч.",
  "excursion_days": "Дни проведения",
  "excursion_days_not_specified": "Дни проведения: не указаны",
  "excursion_pickup_time": "Время сбора на экскурсию",
  "show_info": "Показать информацию",
  "open_in_google_maps": "Открыть в Google Maps",
  "adult_price": "Цена взрослого билета",
  "child_price": "Цена детского билета (от 3 до 11 лет)",
  "child_free_note": "Дети от 0 до 3-х лет едут бесплатно без права на посадочное место",
  "read_more": "Подробнее",
  "choose_your_hotel": "Выберите ваш отель проживания",
  "mon": "пн",
  "tue": "вт",
  "wed": "ср",
  "thu": "чт",
  "fri": "пт",
  "sat": "сб",
  "sun": "вс",
  "ask_question": "Задать вопрос",
  "ask_intro": "Если вы не нашли нужную информацию, напишите нам — мы ответим в ближайшее время.",
  "your_name": "Ваше имя",
  "question_category": "Категория вопроса",
  "select_category": "Выберите категорию",
  "category_transfer": "Вопрос по трансферу",
  "category_excursion": "Вопрос по экскурсии",
  "category_organization": "Организационный вопрос",
  "category_other": "Другое",
  "your_question": "Ваш вопрос",
  "send_question": "Отправить вопрос",
  "success_message": "Ваш вопрос успешно отправлен. Мы свяжемся с вами в ближайшее время.",
  "error_message": "Произошла ошибка при отправке. Попробуйте позже.",
  "no_excursion_for_hotel": "Для этого отеля нет подходящих экскурсий. Свяжитесь с нашим представителем.",
  "contacts_intro": "Свяжитесь с нами любым удобным способом. Мы всегда готовы помочь вам с вопросами по экскурсиям, трансферам и другой информации.",
  "about_intro": "Наш проект создан для того, чтобы сделать ваш отдых на Коста-дель-Соль максимально комфортным. Здесь вы найдете всю необходимую информацию о трансферах, экскурсиях, инфо-встречах и полезные советы для туристов.",
  "contacts_title": "Наши контакты",
  "contacts_intro": "Свяжитесь с нами любым удобным способом. Мы всегда готовы помочь вам с вопросами по экскурсиям, трансферам и другой информации.",
  "contacts_email": "Электронная почта",
  "contacts_whatsapp": "WhatsApp",
  "contacts_telegram": "Telegram",
  "contacts_working_hours": "Часы работы",
  "contacts_social": "Мы в соцсетях",
  "contacts_form_title": "Напишите нам",
  "contacts_form_name": "Ваше имя",
  "contacts_form_email": "Ваш email",
  "contacts_form_message": "Сообщение",
  "contacts_form_send": "Отправить сообщение",
  "contacts_form_success": "Спасибо! Сообщение отправлено, мы ответим в ближайшее время.",
  "contacts_form_error": "Не удалось отправить сообщение. Попробуйте позже.",
  "our_team": "Наша команда",
  "transfer_time_pending": "Время трансфера пока не назначено. Пожалуйста, попробуйте позже или свяжитесь с нашим представителем",
  "group_transfer_time_pending": "На выбранную дату время группового трансфера ещё не назначено. Попробуйте позже или свяжитесь с нашим представителем.",
  "private_transfer_time_pending": "Время индивидуального трансфера ещё не назначено. Пожалуйста, попробуйте позже или оставьте e-mail для уведомления.",
  "excursion": {
    "child_free_note": "Дети от 0 до 3-х лет едут бесплатно без права на посадочное место едут на руках у родителей",
    "select_hotel_title": "Чтобы узнать место сбора и стоимость поездки — выберите ваш отель",
    "select_hotel_instruction": "Введите название отеля и выберите из списка ниже",
    "select_hotel_placeholder": "Начните вводить название отеля"
  },
  "cookies": {
    "title": "Мы используем cookies",
    "desc": "Обязательные cookies помогают сайту работать. Аналитика и маркетинг — только с вашего согласия. Вы можете изменить выбор позже в «Настройках cookies».",
    "essential": "Обязательные",
    "analytics": "Аналитика",
    "marketing": "Маркетинг",
    "preferences": "Предпочтения (удобства)",
    "accept_all": "Принять все",
    "reject_all": "Отклонить все",
    "save": "Сохранить выбор",
    "settings": "Настройки печенек"
  }
}

```

---
## frontend/src/locales/en/translation.json

```json
{
  "home": "Home",
  "excursions": "Excursions",
  "info_meeting": "Info Meeting",
  "airport_transfer": "Airport Transfer",
  "ask": "Ask a Question",
  "contacts": "Contacts",
  "about": "About Us",
  "transfer_to_airport": "Select Your Transfer Type",
  "group_transfer": "Group Transfer",
  "private_transfer": "Private Transfer",
  "please_enter_last_name": "Please enter your last name",
  "enter_hotel_and_date": "Specify the hotel and departure date to get the exact transfer time",
  "enter_hotel": "Enter the hotel name",
  "select_date": "Select the transfer date",
  "show_transfer_time": "Show Transfer Time",
  "pickup_time": "Pickup Time",
  "pickup_point": "Pickup Point",
  "please_fill_all_fields": "Please fill in all fields",
  "something_went_wrong": "An error occurred. Please try again.",
  "want_to_receive_email": "Would you like to receive this information via email?",
  "email_info_text": "We will send you the transfer time and a map link. If there are any changes, you will receive a new email.",
  "enter_email": "Enter your email",
  "consent_text": "I have read and agree to the terms and privacy policy",
  "footer_tagline": "Your Guide to Costa del Sol",
  "footer_nav_title": "Navigation",
  "footer_rights": "All rights reserved.",
  "send_to_email": "Send to Email",
  "email_sent_success": "Information successfully sent to your email!",
  "email_send_error": "Error sending email. Please try again later.",
  "enter_last_name": "Last Name",
  "your_last_name": "Enter your last name",
  "find_my_transfer": "Check Transfer",
  "no_transfer_found": "Transfer not found. Contact the representative.",
  "did_you_mean": "Did you mean",
  "not_found_contact_us": "If you cannot find your last name, contact the representative:",
  "open_contact_form": "Open Request Form",
  "your_hotel": "Hotel of Stay",
  "departure_date": "Departure Date",
  "flight_number": "Flight Number (if available)",
  "question": "Your Question",
  "your_email": "Email",
  "send_request": "Send Request",
  "request_sent_successfully": "Your request has been successfully sent. We will verify the information and contact you via email.",
  "request_error": "An error occurred while sending the request.",
  "no_transfer_schedule_for_this_date": "No transfer is available for the selected date or hotel. You can send a request below.",
  "no_transfer_for_lastname": "No transfer found for the specified last name. You can clarify the information via the form.",
  "no_transfer_found_message": "No transfer data available for the selected date or hotel. You can send a request below for clarification.",
  "enter_your_email_label": "Enter Your Email",
  "enter_your_lastname_label": "Specify Your Last Name",
  "i_agree_with": "I agree with",
  "terms_and_privacy": "terms and privacy policy",
  "privacy_policy": "Privacy Policy",
  "privacy_policy_text": "The privacy policy will be added later. This section will describe how we store and process your data.",
  "close": "Close",
  "loading": "Loading",
  "policy_not_found": "Policy not found",
  "error_loading_policy": "Error loading policy",
  "info_meeting_title": "Info Meeting",
  "select_hotel": "Select your hotel:",
  "choose_hotel_placeholder": "Start typing the hotel name",
  "check_schedule": "Check Schedule",
  "date": "Date",
  "time_from": "From",
  "time_to": "To",
  "no_meetings_found": "No meetings are scheduled for the selected hotel yet.",
  "no_excursions_found": "No excursions found",
  "duration": "Duration",
  "hours": "hrs",
  "excursion_days": "Excursion Days",
  "excursion_days_not_specified": "Excursion Days: not specified",
  "excursion_pickup_time": "Excursion Pickup Time",
  "show_info": "Show Information",
  "open_in_google_maps": "Open in Google Maps",
  "adult_price": "Adult Ticket Price",
  "child_price": "Child Ticket Price (ages 3 to 11)",
  "child_free_note": "Children aged 0 to 3 travel free without a seat",
  "read_more": "Read More",
  "choose_your_hotel": "Select your hotel of stay",
  "mon": "Mon",
  "tue": "Tue",
  "wed": "Wed",
  "thu": "Thu",
  "fri": "Fri",
  "sat": "Sat",
  "sun": "Sun",
  "ask_question": "Ask a Question",
  "ask_intro": "If you couldn’t find the information you need, write to us — we’ll respond as soon as possible.",
  "your_name": "Your Name",
  "question_category": "Question Category",
  "select_category": "Select Category",
  "category_transfer": "Transfer Question",
  "category_excursion": "Excursion Question",
  "category_organization": "Organizational Question",
  "category_other": "Other",
  "your_question": "Your Question",
  "send_question": "Send Question",
  "success_message": "Your question has been successfully sent. We will contact you soon.",
  "error_message": "An error occurred while sending. Please try again later.",
  "no_excursion_for_hotel": "No suitable excursions for this hotel. Contact your representative.",
  "contacts_intro": "Contact us in any convenient way. We are always ready to assist with questions about excursions, transfers, and other information.",
  "about_intro": "Our project is designed to make your vacation on the Costa del Sol as comfortable as possible. Here you will find all the necessary information about transfers, excursions, info meetings, and useful tips for tourists.",
  "contacts_title": "Our Contacts",
  "contacts_email": "Email",
  "contacts_whatsapp": "WhatsApp",
  "contacts_telegram": "Telegram",
  "contacts_working_hours": "Working Hours",
  "contacts_social": "We are on social media",
  "contacts_form_title": "Write to Us",
  "contacts_form_name": "Your Name",
  "contacts_form_email": "Your Email",
  "contacts_form_message": "Message",
  "contacts_form_send": "Send Message",
  "contacts_form_success": "Thank you! The message has been sent, we will respond soon.",
  "contacts_form_error": "Failed to send the message. Please try again later.",
  "our_team": "Our Team",
  "excursion": {
    "child_free_note": "Children aged 0 to 3 travel free without a seat, on their parents’ lap",
    "select_hotel_title": "To find out the pickup point and trip cost, select your hotel",
    "select_hotel_instruction": "Enter the hotel name and select from the list below",
    "select_hotel_placeholder": "Start typing the hotel name"
  },
  "cookies": {
    "title": "We use cookies",
    "desc": "Essential cookies help the site function. Analytics and marketing cookies are used only with your consent. You can change your choice later in 'Cookie Settings'.",
    "essential": "Essential",
    "analytics": "Analytics",
    "marketing": "Marketing",
    "preferences": "Preferences (convenience)",
    "accept_all": "Accept All",
    "reject_all": "Reject All",
    "save": "Save Selection",
    "settings": "Cookie Settings"
  }
}

```

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


class AskPageContent(models.Model):
    # Заголовки
    title_ru = models.CharField(max_length=255, blank=True, default="")
    title_en = models.CharField(max_length=255, blank=True, default="")
    title_es = models.CharField(max_length=255, blank=True, default="")
    title_uk = models.CharField(max_length=255, blank=True, default="")
    title_lt = models.CharField(max_length=255, blank=True, default="")
    title_lv = models.CharField(max_length=255, blank=True, default="")
    title_et = models.CharField(max_length=255, blank=True, default="")

    # Содержимое (RichText)
    content_ru = models.TextField(blank=True, default="")
    content_en = models.TextField(blank=True, default="")
    content_es = models.TextField(blank=True, default="")
    content_uk = models.TextField(blank=True, default="")
    content_lt = models.TextField(blank=True, default="")
    content_lv = models.TextField(blank=True, default="")
    content_et = models.TextField(blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Контент страницы «Задать вопрос»"
        verbose_name_plural = "Контент страницы «Задать вопрос»"

    # Универсальная выдача локализованных полей с фолбэком
    def get_localized(self, lang: str):
        lang = (lang or "ru").lower().split("-")[0]
        t = getattr(self, f"title_{lang}", "") or self.title_ru or self.title_en or ""
        c = getattr(self, f"content_{lang}", "") or self.content_ru or self.content_en or ""
        return {"title": t, "content": c}


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




# Модель правил на экскурсиях
LANG_CHOICES = [
    ("en", "English"),
    ("es", "Español"),
    ("lt", "Lietuvių"),
    ("lv", "Latviešu"),
    ("et", "Eesti"),
    ("ru", "Русский"),
    ("uk", "Українська"),
]

class ExcursionRules(models.Model):
    language_code = models.CharField(
        "Language code", max_length=5, choices=LANG_CHOICES, unique=True
    )
    title = models.CharField("Title", max_length=255, default="Правила поведения на экскурсиях")
    content = RichTextField("Content (HTML)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Excursion rules"
        verbose_name_plural = "Excursion rules"
        ordering = ["language_code"]

    def __str__(self):
        return dict(LANG_CHOICES).get(self.language_code, self.language_code)


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


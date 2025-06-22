from django.db import models

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
    subtitle = models.TextField(verbose_name="Подзаголовок")
    banner_image = models.ImageField(upload_to='uploads/homepage/', verbose_name="Баннер")

    def __str__(self):
        return "Главная страница"

    class Meta:
        verbose_name = "Главная"
        verbose_name_plural = "Главная"

# Инфо встреча
class InfoMeeting(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    location = models.CharField(max_length=255, blank=True)

    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"InfoMeeting on {self.date} at {self.time}"

    class Meta:
        verbose_name = "Инфо встреча"
        verbose_name_plural = "Инфо встречи"


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

# Детальный трансфер по категориям и отелям
class TransferSchedule(models.Model):
    TRANSFER_TYPE_CHOICES = [
        ('group', 'Групповой'),
        ('private', 'Индивидуальный'),
    ]

    transfer_type = models.CharField(
        max_length=10,
        choices=TRANSFER_TYPE_CHOICES,
        verbose_name="Тип трансфера"
    )

    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, verbose_name="Отель")
    departure_date = models.DateField(verbose_name="Дата выезда")
    departure_time = models.TimeField(verbose_name="Время выезда")

    pickup_point = models.ForeignKey('PickupPoint', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Точка сбора")

    # Только для индивидуального трансфера:
    passenger_last_name = models.CharField(max_length=100, blank=True, verbose_name="Фамилия туриста (если нужно)")

    def __str__(self):
        return f"{self.get_transfer_type_display()} | {self.hotel.name} | {self.departure_date}"

    class Meta:
        verbose_name = "Расписание трансфера"
        verbose_name_plural = "Расписания трансферов"
        ordering = ['departure_date', 'departure_time']


# Задать вопрос
class Question(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question from {self.name}"

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

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

    pickup_point = models.ForeignKey(
        'PickupPoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_hotel',  # 👈 добавлено
        verbose_name="Точка сбора"
    )

    hotel = models.OneToOneField(
        'Hotel',
        on_delete=models.CASCADE,
        related_name='assigned_pickup_point',
        verbose_name='Отель (для трансфера)',
        null=True,  # <--- добавь это!
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"

# Модель точки сбора 
class PickupPoint(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название точки сбора")
    location_description = models.TextField(blank=True, null=True, verbose_name="Описание/примечание")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    region = models.CharField(max_length=100, verbose_name="Регион")
    hotel = models.OneToOneField(
        'Hotel',
        on_delete=models.CASCADE,
        verbose_name="Отель",
        related_name='pickup_transfer',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Точка сбора"
        verbose_name_plural = "Точки сбора"

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
    description = models.TextField(verbose_name="Описание")
    duration = models.PositiveIntegerField(verbose_name="Продолжительность (часы)")
    image = models.ImageField(upload_to='excursions/', blank=True, null=True, verbose_name="Главное изображение")
    days = models.JSONField(verbose_name="Дни недели", help_text="Список дней: mon, tue и т.д.")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"


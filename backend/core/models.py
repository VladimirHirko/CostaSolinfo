from django.db import models

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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Инфо встреча"
        verbose_name_plural = "Инфо встречи"

# Трансфер в аэропорт 
class AirportTransfer(models.Model):
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    contact_email = models.EmailField()

    def __str__(self):
        return f"Transfer - {self.price} €"

    class Meta:
        verbose_name = "Трансфер в аэропорт"
        verbose_name_plural = "Трансферы в аэропорт"

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

# Отели
class Hotel(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название отеля")
    region = models.CharField(max_length=100, verbose_name="Регион")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес")
    latitude = models.FloatField(blank=True, null=True, verbose_name="Широта")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Долгота")

    pickup_point = models.ForeignKey(
        'PickupPoint',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Точка сбора"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"

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


# Модель точки сбора 
class PickupPoint(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название точки сбора")
    location_description = models.TextField(blank=True, null=True, verbose_name="Описание/примечание")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    region = models.CharField(max_length=100, verbose_name="Регион")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Точка сбора"
        verbose_name_plural = "Точки сбора"

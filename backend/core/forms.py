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
        required=False  # ⬅️ позволяем временно не выбирать дни
    )

    class Meta:
        model = Excursion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        value = getattr(self.instance, "days", None)
        initial = []
        if isinstance(value, (list, tuple)):
            initial = list(value)
        elif isinstance(value, str) and value.strip():
            # если вдруг хранится строка "mon,wed"
            initial = [v.strip() for v in value.split(",") if v.strip()]
        self.fields["days"].initial = initial

    def clean_days(self):
        """
        Возвращаем список кодов дней в правильном порядке (mon..sun).
        """
        selected = self.cleaned_data.get('days') or []
        allowed = {'mon','tue','wed','thu','fri','sat','sun'}
        selected = [d for d in selected if d in allowed]

        order = ['mon','tue','wed','thu','fri','sat','sun']
        selected_sorted = [d for d in order if d in selected]
        return selected_sorted  # сохранится как список (JSONField/ArrayField)

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
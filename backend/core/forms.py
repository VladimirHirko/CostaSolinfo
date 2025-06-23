from django import forms
from .models import Excursion, Hotel, TransferSchedule, PickupPoint
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
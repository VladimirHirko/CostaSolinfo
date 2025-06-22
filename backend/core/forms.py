from django import forms
from .models import Excursion

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


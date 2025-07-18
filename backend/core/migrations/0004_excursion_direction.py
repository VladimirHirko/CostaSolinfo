# Generated by Django 5.2.3 on 2025-06-21 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_pickuppoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='excursion',
            name='direction',
            field=models.CharField(choices=[('MALAGA_TO_GIB', 'От Малаги к Гибралтару'), ('GIB_TO_MALAGA', 'От Гибралтара к Малаге')], default='MALAGA_TO_GIB', max_length=20, verbose_name='Направление маршрута'),
        ),
    ]

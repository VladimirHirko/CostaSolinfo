# Generated by Django 5.2.3 on 2025-06-28 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_transfernotification_departure_time_sent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hotel_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('old_time', models.TimeField()),
                ('new_time', models.TimeField()),
                ('changed_by', models.CharField(max_length=150)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.transferschedule')),
            ],
        ),
    ]

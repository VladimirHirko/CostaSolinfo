# Generated by Django 5.2.3 on 2025-06-23 17:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_pickuppoint_hotel'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupTransferPickupPoint',
            fields=[
            ],
            options={
                'verbose_name': 'Точка сбора (Групповой трансфер)',
                'verbose_name_plural': 'Точки сбора для группового трансфера',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.pickuppoint',),
        ),
        migrations.CreateModel(
            name='PrivateTransferPickupPoint',
            fields=[
            ],
            options={
                'verbose_name': 'Точка сбора (Индивидуальный трансфер)',
                'verbose_name_plural': 'Точки сбора для индивидуального трансфера',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('core.pickuppoint',),
        ),
    ]

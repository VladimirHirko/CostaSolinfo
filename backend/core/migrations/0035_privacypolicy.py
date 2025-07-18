# Generated by Django 5.2.3 on 2025-07-13 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_transferinquiry_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(choices=[('ru', 'Русский'), ('en', 'English'), ('es', 'Español'), ('lt', 'Lietuvių'), ('lv', 'Latviešu'), ('et', 'Eesti'), ('uk', 'Українська')], max_length=5, unique=True)),
                ('content', models.TextField(verbose_name='Текст политики')),
            ],
        ),
    ]

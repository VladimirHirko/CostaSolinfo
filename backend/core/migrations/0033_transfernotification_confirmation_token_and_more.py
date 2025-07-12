from django.db import migrations, models
import uuid

def generate_tokens(apps, schema_editor):
    TransferNotification = apps.get_model('core', 'TransferNotification')
    for obj in TransferNotification.objects.all():
        obj.confirmation_token = uuid.uuid4()
        obj.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_transfernotification_last_name_alter_pagebanner_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfernotification',
            name='confirmation_token',
            field=models.UUIDField(null=True, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='transfernotification',
            name='is_changed',
            field=models.BooleanField(default=False, verbose_name='Трансфер изменен'),
        ),
        migrations.AddField(
            model_name='transfernotification',
            name='is_confirmed',
            field=models.BooleanField(default=False, verbose_name='Клиент подтвердил получение'),
        ),
        migrations.RunPython(generate_tokens),
        migrations.AlterField(
            model_name='transfernotification',
            name='confirmation_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_remove_excursioncontentblock_content_en_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='excursionpickuppoint',
            name='direction',
            field=models.CharField(
                max_length=20,
                choices=[('malaga', 'В сторону Малаги'), ('gibraltar', 'В сторону Гибралтара')],
                default='malaga',
                verbose_name='Направление'
            ),
            preserve_default=False,
        ),
    ]

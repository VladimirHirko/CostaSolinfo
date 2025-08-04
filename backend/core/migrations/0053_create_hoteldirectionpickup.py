from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_merge_20250803_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='HotelDirectionPickup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")),
                ('longitude', models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")),
                ('direction', models.CharField(
                    max_length=20,
                    choices=[('malaga', 'В сторону Малаги'), ('gibraltar', 'В сторону Гибралтара')],
                    default='malaga',
                    verbose_name="Направление"
                )),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hotel')),
            ],
        ),
    ]

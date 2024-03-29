# Generated by Django 3.2.7 on 2021-09-08 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_auto_20210607_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='training_type',
            field=models.CharField(choices=[('NEURAL_CIRCUIT', 'Neural Circuit'), ('MILITAR', 'Militar Box'), ('POWER_HOUR', 'Power Hour'), ('BALANCE', 'Balance'), ('WORKOUT', 'Workout Energy'), ('VIRTUAL', 'Virtual'), ('SPECIAL', 'Special class')], default='NEURAL_CIRCUIT', max_length=50),
        ),
    ]

# Generated by Django 3.2.10 on 2022-12-31 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0019_imagepopup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='training_type',
            field=models.CharField(choices=[('FUNCIONAL_TRAINING', 'Funcional Training'), ('GAP_MMSS', 'GAP/MMSS'), ('CARDIO_STEP', 'Aeroibic Step'), ('SENIOR', 'Senior'), ('RTG', 'RTG'), ('PILATES', 'Pilates'), ('FIT_BOXING', 'Funcional box'), ('BALANCE', 'Balance'), ('SUPERSTAR', 'Super Star'), ('CARDIOHIT', 'Cardio Hit'), ('A_FUEGO', 'Solo pernil'), ('RUMBA', 'Rumba')], default='FUNCIONAL_TRAINING', max_length=50),
        ),
    ]

# Generated by Django 3.2.16 on 2022-12-30 07:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_ranking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rankings', to=settings.AUTH_USER_MODEL),
        ),
    ]

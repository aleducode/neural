"""Tipo de notificación para los módulos de videos.

Avisar de un módulo nuevo con el tipo «general» lo mezclaba con todo lo demás
en la pantalla de notificaciones del panel, que filtra por tipo.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("users", "0031_phone_number_nullable")]

    operations = [
        migrations.AlterField(
            model_name="pushnotification",
            name="notification_type",
            field=models.CharField(choices=[("general", "General"), ("training_reminder", "Recordatorio de entrenamiento"), ("training_cancelled", "Entrenamiento cancelado"), ("membership_expiring", "Membresía por vencer"), ("membership_expired", "Membresía vencida"), ("achievement", "Logro desbloqueado"), ("promotion", "Promoción"), ("community", "Comunidad"), ("video_package", "Módulo de videos")], default="general", max_length=30),
        ),
    ]

"""Quien asigno el modulo.

La app firma la nota del entrenador con su nombre. Nulo en lo ya asignado:
esas filas se crearon antes de que el campo existiera.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("training", "0032_video_stream"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="packageassignment",
            name="assigned_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="packages_assigned", to=settings.AUTH_USER_MODEL, verbose_name="Asignado por"),
        ),
    ]

"""El telefono puede faltar.

La columna es unica y no admitia nulos, asi que la cadena vacia solo cabia en
una cuenta: guardar la ficha de un segundo usuario sin telefono fallaba con
IntegrityError. Varios NULL no chocan entre si.
"""

import django.core.validators
from django.db import migrations, models


def vaciar_a_null(apps, schema_editor):
    User = apps.get_model("users", "User")
    User.objects.filter(phone_number="").update(phone_number=None)


def null_a_vacio(apps, schema_editor):
    User = apps.get_model("users", "User")
    # Solo la primera: la columna es unica y no caben dos cadenas vacias.
    primero = User.objects.filter(phone_number__isnull=True).first()
    if primero:
        primero.phone_number = ""
        primero.save(update_fields=["phone_number"])


class Migration(migrations.Migration):
    dependencies = [("users", "0030_ticket_packs")]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=17, null=True, unique=True, validators=[django.core.validators.RegexValidator(message="phone number must be entered in the format +99999999999", regex="\\+?1?\\d{9,15}$")]),
        ),
        migrations.RunPython(vaciar_a_null, null_a_vacio),
    ]

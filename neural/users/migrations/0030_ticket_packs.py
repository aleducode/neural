"""Tiqueteras: planes que se miden en sesiones y no solo en dias.

Recepcion vende paquetes de 4, 8 y 12 clases con 30 dias para usarlas. El
modelo solo sabia de duracion, asi que se agrega el numero de sesiones --en el
plan y, copiado, en la membresia-- y un tipo nuevo.

Los tres planes nacen con precio 0: los pone el gimnasio.
"""

from django.db import migrations, models

TIQUETERAS = [
    ("Tiquetera 4", 4),
    ("Tiquetera 8", 8),
    ("Tiquetera 12", 12),
]


def crear_tiqueteras(apps, schema_editor):
    NeuralPlan = apps.get_model("users", "NeuralPlan")
    for nombre, sesiones in TIQUETERAS:
        NeuralPlan.objects.update_or_create(
            slug_name=nombre.lower().replace(" ", "_"),
            defaults={
                "name": nombre,
                "description": f"{sesiones} clases para agendar en 30 días.",
                "price": 0,
                "duration": 30,
                "sessions": sesiones,
            },
        )


def borrar_tiqueteras(apps, schema_editor):
    NeuralPlan = apps.get_model("users", "NeuralPlan")
    NeuralPlan.objects.filter(
        slug_name__in=[n.lower().replace(" ", "_") for n, _ in TIQUETERAS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("users", "0029_passwordresetcode")]

    operations = [
        migrations.AddField(
            model_name="neuralplan",
            name="sessions",
            field=models.PositiveIntegerField(default=0, help_text="0 = plan por tiempo, sin tope de reservas. Mayor que 0 = tiquetera.", verbose_name="Sesiones incluidas"),
        ),
        migrations.AddField(
            model_name="usermembership",
            name="sessions_total",
            field=models.PositiveIntegerField(default=0, help_text="Copia del plan al activarlo. 0 = plan por tiempo.", verbose_name="Sesiones compradas"),
        ),
        migrations.AlterField(
            model_name="usermembership",
            name="membership_type",
            field=models.CharField(choices=[("MENSUAL", "Mensualidad"), ("QUARTER", "Trimestre"), ("SEMESTER", "Semestre"), ("TICKETS", "Tiquetera")], default="MENSUAL", max_length=10),
        ),
        migrations.RunPython(crear_tiqueteras, borrar_tiqueteras),
    ]

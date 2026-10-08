"""Un tipo para los planes que no son ninguno de los tres historicos.

Al poder crear planes desde el panel --"Clientes nuevos 15 dias", por
ejemplo-- hacia falta donde ponerlos: sin esto caian en "Tiquetera", que es
otra cosa.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("users", "0032_video_package_notification")]

    operations = [
        migrations.AlterField(
            model_name="usermembership",
            name="membership_type",
            field=models.CharField(choices=[("MENSUAL", "Mensualidad"), ("QUARTER", "Trimestre"), ("SEMESTER", "Semestre"), ("TICKETS", "Tiquetera"), ("OTHER", "Otro plan")], default="MENSUAL", max_length=10),
        ),
    ]

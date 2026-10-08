"""De que segundo sale la miniatura de cada video.

Salia siempre del segundo 1, y al segundo 1 el entrenador todavia esta parado
sin empezar. Los seis videos se grabaron en la misma sala con la misma
persona, asi que las seis miniaturas se veian practicamente iguales.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("training", "0034_assignment_author")]

    operations = [
        migrations.AddField(
            model_name="video",
            name="poster_second",
            field=models.PositiveIntegerField(default=1, help_text="De qué momento del video sale la miniatura. En el segundo 1 casi nadie empezó todavía: elegí uno donde se vea el movimiento.", verbose_name="Segundo de la miniatura"),
        ),
    ]

"""Las seis tablas de video nacieron con id integer en lugar de bigint.

Los modelos no declaran pk, asi que heredan DEFAULT_AUTO_FIELD = BigAutoField.
Las migraciones 0030 y 0031 se generaron con otros settings y escribieron
AutoField, de modo que cada `migrate` avisaba de un cambio sin migracion. Las
tablas estan vacias, asi que el ALTER es inmediato.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("training", "0032_video_stream")]

    operations = [
        migrations.AlterField(
            model_name="packageassignment",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="packagevideo",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="video",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="videopackage",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="videoprogress",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="videoupload",
            name="id",
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("training", "0031_videoupload")]

    operations = [
        migrations.AddField(
            model_name="video",
            name="stream_uid",
            field=models.CharField(blank=True, db_index=True, default="", max_length=64, verbose_name="UID en Cloudflare Stream"),
        ),
        migrations.AddField(
            model_name="video",
            name="stream_ready",
            field=models.BooleanField(default=False, verbose_name="Listo en Stream"),
        ),
        migrations.AlterField(
            model_name="video",
            name="source",
            field=models.CharField(choices=[("url", "Enlace"), ("stream", "Cloudflare Stream"), ("upload", "Archivo subido")], default="url", max_length=10, verbose_name="Fuente"),
        ),
        migrations.AddField(
            model_name="videoupload",
            name="direct_url",
            field=models.URLField(blank=True, default="", max_length=1000, verbose_name="URL de subida directa"),
        ),
        migrations.AddField(
            model_name="videoupload",
            name="stream_uid",
            field=models.CharField(blank=True, default="", max_length=64, verbose_name="UID en Stream"),
        ),
    ]

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("training", "0030_videos")]

    operations = [
        migrations.CreateModel(
            name="VideoUpload",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("token", models.CharField(db_index=True, max_length=64, unique=True, verbose_name="Token")),
                ("filename", models.CharField(max_length=255, verbose_name="Nombre del archivo")),
                ("size", models.PositiveBigIntegerField(verbose_name="Tamaño total")),
                ("chunk_size", models.PositiveIntegerField(verbose_name="Tamaño del trozo")),
                ("received", models.JSONField(default=list, verbose_name="Trozos recibidos")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Completada")),
                ("video", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="uploads", to="training.video")),
            ],
            options={"verbose_name": "Subida de video", "verbose_name_plural": "Subidas de video", "ordering": ["-created"]},
        ),
    ]

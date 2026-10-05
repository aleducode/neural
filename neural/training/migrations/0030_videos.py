import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("training", "0029_trainingtype_photo"),
        ("users", "0029_passwordresetcode"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Video",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("name", models.CharField(max_length=255, verbose_name="Nombre")),
                ("description", models.TextField(blank=True, default="", verbose_name="Descripción")),
                ("source", models.CharField(choices=[("url", "Enlace"), ("upload", "Archivo subido")], default="url", max_length=10, verbose_name="Fuente")),
                ("url", models.URLField(blank=True, default="", max_length=500, verbose_name="Enlace")),
                ("file", models.FileField(blank=True, null=True, upload_to="videos/", verbose_name="Archivo")),
                ("thumbnail", models.ImageField(blank=True, null=True, upload_to="videos/thumbs/", verbose_name="Miniatura")),
                ("duration_seconds", models.PositiveIntegerField(default=0, verbose_name="Duración (s)")),
                ("level", models.CharField(choices=[("all", "Todos los niveles"), ("beginner", "Principiante"), ("intermediate", "Intermedio"), ("advanced", "Avanzado")], default="all", max_length=20, verbose_name="Nivel")),
                ("is_published", models.BooleanField(default=False, verbose_name="Publicado")),
                ("training_type", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="videos", to="training.trainingtype")),
            ],
            options={"verbose_name": "Video", "verbose_name_plural": "Videos", "ordering": ["-created"]},
        ),
        migrations.CreateModel(
            name="VideoPackage",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("name", models.CharField(max_length=255, verbose_name="Nombre")),
                ("description", models.TextField(blank=True, default="", verbose_name="Descripción")),
                ("cover", models.ImageField(blank=True, null=True, upload_to="packages/", verbose_name="Portada")),
                ("kind", models.CharField(choices=[("group", "Grupal"), ("individual", "Individual")], default="group", max_length=15, verbose_name="Modalidad")),
                ("is_published", models.BooleanField(default=False, verbose_name="Publicado")),
            ],
            options={"verbose_name": "Paquete de videos", "verbose_name_plural": "Paquetes de videos", "ordering": ["-created"]},
        ),
        migrations.CreateModel(
            name="PackageVideo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Orden")),
                ("notes", models.CharField(blank=True, default="", max_length=500, verbose_name="Notas del entrenador")),
                ("package", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="training.videopackage")),
                ("video", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="training.video")),
            ],
            options={"verbose_name": "Video del paquete", "verbose_name_plural": "Videos del paquete", "ordering": ["order", "id"]},
        ),
        migrations.AddField(
            model_name="videopackage",
            name="videos",
            field=models.ManyToManyField(related_name="packages", through="training.PackageVideo", to="training.video"),
        ),
        migrations.CreateModel(
            name="PackageAssignment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("everyone", models.BooleanField(default=False, verbose_name="Para todos")),
                ("package", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="training.videopackage")),
                ("plan", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="video_packages", to="users.neuralplan")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="video_packages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Asignación de paquete", "verbose_name_plural": "Asignaciones de paquetes", "ordering": ["-created"]},
        ),
        migrations.CreateModel(
            name="VideoProgress",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, help_text="Date time on which the object was created.", verbose_name="created at")),
                ("modified", models.DateTimeField(auto_now=True, help_text="Date time on which the object was last modified.", verbose_name="modified at")),
                ("seconds", models.PositiveIntegerField(default=0, verbose_name="Segundos vistos")),
                ("completed_at", models.DateTimeField(blank=True, null=True, verbose_name="Completado")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="video_progress", to=settings.AUTH_USER_MODEL)),
                ("video", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress", to="training.video")),
            ],
            options={"verbose_name": "Progreso de video", "verbose_name_plural": "Progreso de videos", "ordering": ["-modified"]},
        ),
        migrations.AddConstraint(
            model_name="packagevideo",
            constraint=models.UniqueConstraint(fields=("package", "video"), name="unique_video_per_package"),
        ),
        migrations.AddConstraint(
            model_name="packageassignment",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(("everyone", False), ("plan__isnull", True), ("user__isnull", False))
                    | models.Q(("everyone", False), ("plan__isnull", False), ("user__isnull", True))
                    | models.Q(("everyone", True), ("plan__isnull", True), ("user__isnull", True))
                ),
                name="assignment_has_exactly_one_target",
            ),
        ),
        migrations.AddConstraint(
            model_name="videoprogress",
            constraint=models.UniqueConstraint(fields=("user", "video"), name="unique_progress_per_user_video"),
        ),
    ]

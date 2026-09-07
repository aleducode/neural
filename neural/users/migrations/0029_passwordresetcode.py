import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0028_profile_hide_from_leaderboard"),
    ]

    operations = [
        migrations.CreateModel(
            name="PasswordResetCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date time on which the object was created.",
                        verbose_name="created at",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Date time on which the object was last modified.",
                        verbose_name="modified at",
                    ),
                ),
                ("code_hash", models.CharField(max_length=128)),
                ("expires_at", models.DateTimeField()),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("token_hash", models.CharField(blank=True, default="", max_length=128)),
                ("token_expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reset_codes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Código de recuperación",
                "verbose_name_plural": "Códigos de recuperación",
                "ordering": ["-created"],
            },
        ),
    ]

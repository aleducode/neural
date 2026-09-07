from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0027_remove_userstats_unique_stats_alter_userstats_year_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="hide_from_leaderboard",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Saca al socio del ranking de comunidad. No solo lo esconde: "
                    "deja de contar para las posiciones de los demás."
                ),
                verbose_name="Ocultar del ranking",
            ),
        ),
    ]

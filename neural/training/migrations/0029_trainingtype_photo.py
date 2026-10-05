from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("training", "0028_rename_class_trainging_slot_class_training"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainingtype",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text="Se ve en el panel, en «Clases más pedidas». 320x352 o mayor.",
                null=True,
                upload_to="training_types/",
                verbose_name="Foto de la clase",
            ),
        ),
    ]

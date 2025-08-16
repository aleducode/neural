"""User model."""

from slugify import slugify

# Django
from django.utils import timezone
from django.db import models

from neural.users.models import User

# Utils
from neural.utils.models import NeuralBaseModel


class Space(NeuralBaseModel):
    slug_name = models.SlugField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.CharField(null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_").lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.description}"


class TrainingType(NeuralBaseModel):
    """Traingin type model."""

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(unique=True, max_length=100)
    is_group = models.BooleanField(default=True)

    def __str__(self):
        """Return training type."""
        return self.name

    class Meta:
        """Meta class."""

        verbose_name = "Tipo de entrenamiento"
        verbose_name_plural = "Tipos de entrenamientos"

    def save(self, *args, **kwargs):
        if not self.slug_name:
            self.slug_name = slugify(self.name, separator="-")
        super().save(*args, **kwargs)


class Classes(NeuralBaseModel):
    """Classes model."""

    class DaysChoices(models.TextChoices):
        MONDAY = "MONDAY", "Lunes"
        TUESDAY = "TUESDAY", "Martes"
        WEDNESDAY = "WEDNESDAY", "Miércoles"
        THURSDAY = "THURSDAY", "Jueves"
        FRIDAY = "FRIDAY", "Viernes"
        SATURDAY = "SATURDAY", "Sábado"
        SUNDAY = "SUNDAY", "Domingo"

    day = models.CharField(
        max_length=10, choices=DaysChoices.choices, default=DaysChoices.MONDAY
    )
    training_type = models.ForeignKey(
        TrainingType, on_delete=models.CASCADE, related_name="classes"
    )
    hour_init = models.TimeField()
    hour_end = models.TimeField()

    def __str__(self):
        """Return training type."""
        return f"{self.training_type} - {self.day}"

    class Meta:
        """Meta class."""

        verbose_name = "Calendario de clases"
        verbose_name_plural = "Calendario de clases"
        constraints = [
            models.UniqueConstraint(
                fields=["day", "hour_init", "hour_end", "training_type"],
                name="unique_class_combination",
            )
        ]


class Slot(NeuralBaseModel):
    date = models.DateField()
    max_places = models.IntegerField()
    class_training = models.ForeignKey(
        Classes, on_delete=models.CASCADE, related_name="slots", blank=True, null=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Clase {self.date} - {self.class_training.hour_init} - {self.class_training.hour_end}"

    @property
    def users_scheduled(self):
        return self.user_trainings.filter(status="CONFIRMED")

    @property
    def available_places(self):
        return self.max_places - self.users_scheduled.count()

    @property
    def users(self):
        return self.users_scheduled.all().select_related("user")


class UserTraining(NeuralBaseModel):
    """Gym session model."""

    class Status(models.TextChoices):
        CANCELLED = "CANCELLED", "Cancelada"
        CONFIRMED = "CONFIRMED", "Confirmada"
        DONE = "DONE", "Terminada"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trainings",
        limit_choices_to={"is_verified": True},
    )
    slot = models.ForeignKey(
        Slot, on_delete=models.CASCADE, related_name="user_trainings"
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="user_trainings",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Entrenamiento: {self.user.get_full_name()} - {self.user}"

    @property
    def is_now(self):
        return self.slot.date == timezone.localdate()

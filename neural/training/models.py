"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from neural.users.models import User
# Utils
from neural.utils.models import NeuralBaseModel


class Slot(NeuralBaseModel):

    class TrainingType(models.TextChoices):
        FUNCTIONAL = 'FUNCTIONAL', 'Funcional'
        PERSONAL = 'PERSONAL', 'Personalizado'

    date = models.DateField()
    hour_init = models.TimeField()
    hour_end = models.TimeField()
    max_places = models.IntegerField()
    training_type = models.CharField(
        max_length=50,
        choices=TrainingType.choices,
        default=TrainingType.FUNCTIONAL,
    )

    def __str__(self):
        return f'Clase {self.date} [{self.hour_init}-{self.hour_end}]'

    @property
    def users_scheduled(self):
        return self.user_trainings.filter(status='CONFIRMED')

    @property
    def available_places(self):
        return self.max_places - self.users_scheduled.count()


class UserTraining(NeuralBaseModel):
    """Gym session model."""

    class Status(models.TextChoices):
        CANCELLED = 'CANCELLED', 'Cancelada'
        CONFIRMED = 'CONFIRMED', 'Confirmada'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trainings',
        limit_choices_to={'is_verified': True}
    )
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='user_trainings')
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )

    def __str__(self):
        return f'Entrenamiento: {self.user}'


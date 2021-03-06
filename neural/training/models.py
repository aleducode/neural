"""User model."""

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
        from unidecode import unidecode
        self.slug_name = unidecode(self.name).replace(" ", "_").lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}-{self.description}'


class Slot(NeuralBaseModel):

    class TrainingType(models.TextChoices):
        NEURAL_CIRCUIT = 'NEURAL_CIRCUIT', 'Neural Circuit'
        POWER_HOUR = 'POWER_HOUR', 'Power Hour'
        BALANCE = 'BALANCE', 'Balance'
        WORKOUT = 'WORKOUT', 'Workout Energy'
        VIRTUAL = 'VIRTUAL', 'Virtual'
        SPECIAL = 'SPECIAL', 'Special class'

    date = models.DateField()
    hour_init = models.TimeField()
    hour_end = models.TimeField()
    max_places = models.IntegerField()
    training_type = models.CharField(
        max_length=50,
        choices=TrainingType.choices,
        default=TrainingType.NEURAL_CIRCUIT,
    )

    def __str__(self):
        return f'Clase {self.date} [{self.hour_init}-{self.hour_end}]'

    @property
    def users_scheduled(self):
        return self.user_trainings.filter(status='CONFIRMED')

    @property
    def available_places(self):
        return self.max_places - self.users_scheduled.count()

    @property
    def available_seats(self):
        space = Space.objects.all()
        return space.exclude(id__in=self.users_scheduled.values_list('space', flat=True)).order_by('id')


class UserTraining(NeuralBaseModel):
    """Gym session model."""

    class Status(models.TextChoices):
        CANCELLED = 'CANCELLED', 'Cancelada'
        CONFIRMED = 'CONFIRMED', 'Confirmada'
        DONE = 'DONE', 'Terminada'

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
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='user_trainings', null=True, blank=True)

    def __str__(self):
        return f'Entrenamiento: {self.user}'

    @property
    def random_icon(self):
        import random
        icons = ['bx bx-cycling', 'bx bx-football', 'bx bx-dumbbell']
        index = random.randint(0, len(icons)-1)
        return icons[index]

    @property
    def is_now(self):
        return self.slot.date == timezone.localdate()


class UserTemperature(NeuralBaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='temperatures',
        limit_choices_to={'is_verified': True}
    )
    temperature = models.FloatField()

    def __str__(self):
        return f'Temperatura: {self.user}'

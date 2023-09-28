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
        from unidecode import unidecode
        self.slug_name = unidecode(self.name).replace(" ", "_").lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}-{self.description}'


class TrainingType(NeuralBaseModel):
    """Traingin type model."""

    name = models.CharField(max_length=255)
    slug_name = models.SlugField(unique=True, max_length=100)

    def __str__(self):
        """Return training type."""
        return self.name

    class Meta:
        """Meta class."""

        verbose_name = "Tipo de entrenamiento"
        verbose_name_plural = "Tipos de entrenamientos"

    def save(self, *args, **kwargs):
        if not self.slug_name:
            self.slug_name = slugify(self.name, separator='-')
        super().save(*args, **kwargs)


class Classes(NeuralBaseModel):
    """Classes model."""
    class DaysChoices(models.TextChoices):
        MONDAY = 'MONDAY', 'Lunes'
        TUESDAY = 'TUESDAY', 'Martes'
        WEDNESDAY = 'WEDNESDAY', 'Miércoles'
        THURSDAY = 'THURSDAY', 'Jueves'
        FRIDAY = 'FRIDAY', 'Viernes'
        SATURDAY = 'SATURDAY', 'Sábado'
        SUNDAY = 'SUNDAY', 'Domingo'

    day = models.CharField(max_length=10, choices=DaysChoices.choices, default=DaysChoices.MONDAY)
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE, related_name='classes')
    hour_init = models.TimeField()
    hour_end = models.TimeField()

    def __str__(self):
        """Return training type."""
        return f"{self.training_type} - {self.get_day_display()}"
    
    class Meta:
        """Meta class."""

        verbose_name = "Calendario de clases"
        verbose_name_plural = "Calendario de clases"


class Slot(NeuralBaseModel):

    date = models.DateField()
    max_places = models.IntegerField()
    class_trainging = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='slots', blank=True, null=True)

    def __str__(self):
        return f'Clase {self.date}'

    @property
    def users_scheduled(self):
        return self.user_trainings.filter(status='CONFIRMED')

    @property
    def available_places(self):
        return self.max_places - self.users_scheduled.count()

    @property
    def users(self):
        return self.users_scheduled.all().select_related('user')


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
        return f'Entrenamiento: {self.user.get_full_name()} - {self.user}'

    @property
    def random_icon(self):
        import random
        icons = ['bx bx-cycling', 'bx bx-football', 'bx bx-dumbbell']
        index = random.randint(0, len(icons)-1)
        return icons[index]

    @property
    def is_now(self):
        return self.slot.date == timezone.localdate()


class ImagePopUp(NeuralBaseModel):
    """Image pop up."""

    image_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='pop_ups')
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Image pop up'
        verbose_name_plural = 'Images pop ups'

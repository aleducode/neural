"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Utils
from neural.utils.models import NeuralBaseModel


class User(NeuralBaseModel, AbstractUser):
    """User model.

    Extend from Django abstract user, change the username field to email
    and add some extra info
    """
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exist',
        }
    )
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='phone number must be entered in the format +99999999999'
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client',
        default=True,
    )
    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text='set to true when address email have verified'
    )

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email


class Plan(NeuralBaseModel):
    """Plan model.

    A plan is a set of trainings that a user can
    do in a specific period of time.
    """
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Profile(NeuralBaseModel):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='profile')
    plan = models.ForeignKey('users.Plan', on_delete=models.CASCADE, related_name='profiles')
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    emergency_contact = models.CharField(max_length=500, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=500, blank=True, null=True)
    profession = models.CharField(max_length=500, blank=True, null=True)
    instagram = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return "Profile of {}".format(self.user)


class Ranking(NeuralBaseModel):
    """Ranking model.

    A ranking is a score that a user get for a specific
    uear. It is used to determine the best user for a
    year.
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='rankings')
    position = models.PositiveIntegerField(unique=True)
    trainings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user} - {self.position}'

    class Meta:
        unique_together = ('user', 'position')

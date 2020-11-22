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
        return self.username

    def get_short_name(self):
        return self.username

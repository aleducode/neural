"""User model."""

# Django
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils import timezone

# Utils
from neural.utils.models import NeuralBaseModel


class User(NeuralBaseModel, AbstractUser):
    """User model.

    Extend from Django abstract user, change the username field to email
    and add some extra info
    """

    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={
            "unique": "A user with that email already exist",
        },
    )
    phone_regex = RegexValidator(
        regex=r"\+?1?\d{9,15}$",
        message="phone number must be entered in the format +99999999999",
    )
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True
    )

    photo = models.ImageField(
        "profile picture",
        upload_to="users/photos/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    is_client = models.BooleanField(
        "client",
        default=True,
    )
    is_verified = models.BooleanField(
        "verified",
        default=False,
        help_text="set to true when address email have verified",
    )

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email


class UserMembership(NeuralBaseModel):
    """User membership model."""

    class MembershipType(models.TextChoices):
        """Membership type."""

        MENSUAL = "MENSUAL", "Mensualidad"
        QUARTER = "QUARTER", "Trimestre"
        SEMESTER = "SEMESTER", "Semestre"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    membership_type = models.CharField(
        max_length=10, choices=MembershipType.choices, default=MembershipType.MENSUAL
    )
    is_active = models.BooleanField(
        "Active",
        default=False,
    )
    init_date = models.DateField(
        "Fecha de inicio membresía", auto_now=False, help_text="Inicio de membresía"
    )
    expiration_date = models.DateField(
        "Fecha fin de membresía",
        auto_now=False,
        help_text="Fecha de expiración membresía",
        blank=True,
        null=True,
    )
    days_duration = models.IntegerField(default=30)

    def save(self, *args, **kwargs):
        date_now = timezone.now().date()
        if self.membership_type == self.MembershipType.MENSUAL:
            self.expiration_date = self.init_date + timezone.timedelta(days=30)
        elif self.membership_type == self.MembershipType.QUARTER:
            self.expiration_date = self.init_date + timezone.timedelta(days=90)
        elif self.membership_type == self.MembershipType.SEMESTER:
            self.expiration_date = self.init_date + timezone.timedelta(days=183)
        self.days_duration = (self.expiration_date - date_now).days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User membership {self.user.email} - {self.user.phone_number} - {self.membership_type}"

    class Meta:
        verbose_name = "Membresía de usuario"
        verbose_name_plural = "Membresías de usuarios"
        constraints = [
            models.UniqueConstraint(
                fields=["user"], condition=Q(is_active=True), name="unique_membership"
            )
        ]


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
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="profile"
    )
    plan = models.ForeignKey(
        "users.Plan", on_delete=models.CASCADE, related_name="profiles"
    )
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

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="rankings"
    )
    position = models.PositiveIntegerField(unique=True)
    trainings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.position}"

    class Meta:
        unique_together = ("user", "position")


class UserStrike(NeuralBaseModel):
    """User strike model.

    A strike is a week inline with assistances to the gym.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="strikes"
    )
    weeks = models.PositiveIntegerField(default=0, db_index=True)

    is_current = models.BooleanField("Current", default=False, db_index=True)
    last_week = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Strike"
        verbose_name_plural = "Strikes"
        constraints = [
            models.UniqueConstraint(
                fields=["user"], condition=Q(is_current=True), name="unique_strike"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.weeks} weeks"


class UserStats(NeuralBaseModel):
    """User stats model.

    A stats is a set of data that a user get for a specific
    week. It is used to determine the user performance in a
    week.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="stats", db_index=True
    )
    year = models.PositiveIntegerField(default=timezone.now().year)
    week = models.PositiveIntegerField(default=0, db_index=True)
    trainings = models.PositiveIntegerField(default=0)
    calories = models.PositiveIntegerField(default=0)
    hours = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Stats"
        verbose_name_plural = "Stats"
        constraints = [
            models.UniqueConstraint(fields=["user", "week"], name="unique_stats")
        ]

    def __str__(self):
        return f"{self.user} - {self.week} - {self.trainings} trainings"

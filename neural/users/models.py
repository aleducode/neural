"""User model."""

from slugify import slugify

# Django
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

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


class NeuralPlan(NeuralBaseModel):
    """Neural plan model."""

    name = models.CharField(max_length=100)
    slug_name = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(default=30)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug_name = slugify(self.name, separator="_")
        super().save(*args, **kwargs)

    @property
    def raw_price(self):
        return int(self.price)


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
    plan = models.ForeignKey(
        "users.NeuralPlan",
        on_delete=models.SET_NULL,
        related_name="memberships",
        blank=True,
        null=True,
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

    @property
    def days_left(self):
        date_now = timezone.localdate()
        return (self.expiration_date - date_now).days + 1

    def save(self, *args, **kwargs):
        # Reset cache membership
        now = timezone.localtime()
        cache_key = f"user_membership_{self.user.id}_{now.date()}"
        # Reset cache membership
        cache.delete(cache_key)
        dict_plans = {
            "MENSUAL": "Mensualidad",
            "QUARTER": "Trimestre",
            "SEMESTER": "Semestre",
        }
        self.plan = NeuralPlan.objects.filter(
            name=dict_plans.get(self.membership_type)
        ).last()
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
    photo = models.ImageField(
        "profile picture",
        upload_to="users/photos/",
        blank=True,
        null=True,
    )
    plan = models.ForeignKey(
        "users.Plan",
        on_delete=models.CASCADE,
        related_name="profiles",
        blank=True,
        null=True,
    )
    height = models.PositiveIntegerField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    emergency_contact = models.CharField(max_length=500, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=500, blank=True, null=True)
    profession = models.CharField(max_length=500, blank=True, null=True)
    instagram = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return "Profile of {}".format(self.user)


class UserWeight(NeuralBaseModel):
    """User weight model.

    A weight is a weight that a user has at a specific date.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="weights"
    )
    weight = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user} - {self.weight}"


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
            models.UniqueConstraint(
                fields=["user", "year", "week"], name="unique_stats_per_year"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.week} - {self.trainings} trainings"


class UserPaymentReference(NeuralBaseModel):
    """User payment reference model.

    A payment reference is a reference that a user get for a specific
    payment. It is used to determine the user payment in a
    week.
    """

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="payments"
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    plan = models.ForeignKey(
        "users.NeuralPlan",
        on_delete=models.SET_NULL,
        related_name="payments",
        blank=True,
        null=True,
    )
    data = models.JSONField(blank=True, null=True)

    def apply_membership(self):
        self.is_paid = True
        self.save()
        self.user.memberships.update_or_create(
            plan=self.plan,
            defaults={
                "init_date": timezone.localdate(),
                "is_active": True,
                "expiration_date": timezone.localdate()
                + timedelta(days=self.plan.duration),
            },
        )

    class Meta:
        verbose_name = "Payment reference"
        verbose_name_plural = "Payment references"

    def __str__(self):
        return f"{self.user} - {self.reference} - {self.amount}"


class Device(NeuralBaseModel):
    """Device model for push notifications."""

    class Platform(models.TextChoices):
        IOS = "ios", "iOS"
        ANDROID = "android", "Android"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    token = models.CharField(max_length=500)
    platform = models.CharField(max_length=10, choices=Platform.choices)
    device_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self):
        return f"{self.user} - {self.platform} - {self.device_id[:20]}"


class PushNotification(NeuralBaseModel):
    """Push notification model.

    Stores all notifications sent to users.
    """

    class NotificationType(models.TextChoices):
        GENERAL = "general", "General"
        TRAINING_REMINDER = "training_reminder", "Recordatorio de entrenamiento"
        TRAINING_CANCELLED = "training_cancelled", "Entrenamiento cancelado"
        MEMBERSHIP_EXPIRING = "membership_expiring", "Membresía por vencer"
        MEMBERSHIP_EXPIRED = "membership_expired", "Membresía vencida"
        ACHIEVEMENT = "achievement", "Logro desbloqueado"
        PROMOTION = "promotion", "Promoción"
        COMMUNITY = "community", "Comunidad"

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        SENT = "sent", "Enviada"
        DELIVERED = "delivered", "Entregada"
        FAILED = "failed", "Fallida"
        READ = "read", "Leída"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(blank=True, null=True, help_text="Extra payload data")
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    # For scheduled notifications
    scheduled_for = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} - {self.title[:50]}"

    def mark_as_read(self):
        if self.status != self.Status.READ:
            self.status = self.Status.READ
            self.read_at = timezone.now()
            self.save(update_fields=["status", "read_at", "modified"])


class PushNotificationLog(NeuralBaseModel):
    """Log for push notification requests/responses.

    Stores all API calls to Expo Push service for auditing and debugging.
    """

    class Status(models.TextChoices):
        SUCCESS = "success", "Éxito"
        ERROR = "error", "Error"

    notification = models.ForeignKey(
        PushNotification, on_delete=models.CASCADE, related_name="logs"
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="notification_logs",
        blank=True,
        null=True,
    )
    expo_push_token = models.CharField(max_length=500)

    # Request info
    request_payload = models.JSONField(help_text="Request sent to Expo")

    # Response info
    response_payload = models.JSONField(
        blank=True, null=True, help_text="Response from Expo"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SUCCESS
    )
    expo_receipt_id = models.CharField(max_length=100, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Log de notificación"
        verbose_name_plural = "Logs de notificaciones"

    def __str__(self):
        return f"{self.notification} - {self.status}"

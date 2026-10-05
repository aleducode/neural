"""Manager app forms."""

from django import forms
from django.contrib.auth import authenticate

from neural.users.models import User, PushNotification, Device, Profile
from neural.training.models import (
    Classes,
    PackageAssignment,
    Video,
    VideoPackage,
)


class ManagerLoginForm(forms.Form):
    """Login form for manager panel."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input",
                "placeholder": "admin@example.com",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            # Try to get user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Credenciales inválidas.")

            # Check if user is staff or superuser
            if not (user.is_staff or user.is_superuser):
                raise forms.ValidationError(
                    "No tienes permisos para acceder al panel de administración."
                )

            # Authenticate
            self.user_cache = authenticate(username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Credenciales inválidas.")

            if not self.user_cache.is_active:
                raise forms.ValidationError("Esta cuenta está desactivada.")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class SendNotificationForm(forms.Form):
    """Form to send push notifications."""

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_client=True, devices__is_active=True)
        .distinct()
        .order_by("first_name", "last_name"),
        label="Usuario",
        widget=forms.Select(
            attrs={
                "class": "form-select select2-user",
                "data-placeholder": "Buscar usuario...",
            }
        ),
    )
    title = forms.CharField(
        label="Título",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Título de la notificación",
            }
        ),
    )
    body = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(
            attrs={
                "class": "form-textarea",
                "placeholder": "Escribe el mensaje de la notificación...",
                "rows": 4,
            }
        ),
    )
    notification_type = forms.ChoiceField(
        label="Tipo",
        choices=PushNotification.NotificationType.choices,
        initial=PushNotification.NotificationType.GENERAL,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update queryset to show user info
        self.fields["user"].label_from_instance = (
            lambda obj: f"{obj.first_name} {obj.last_name} ({obj.email})"
        )


class DeviceForm(forms.ModelForm):
    """Form to edit device token."""

    class Meta:
        model = Device
        fields = ["token", "is_active"]
        widgets = {
            "token": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "ExponentPushToken[...]",
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
        }
        labels = {
            "token": "Push Token",
            "is_active": "Activo",
        }


class MemberProfileForm(forms.Form):
    """The member record.

    It touches two models --User and Profile-- so it is not a ModelForm: it saves
    each field where it actually lives. «Documento» is missing because Neural has
    no such field yet; adding it is a migration, not an input."""

    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    birthdate = forms.DateField(required=False)
    height = forms.IntegerField(required=False, min_value=50, max_value=260)
    profession = forms.CharField(max_length=500, required=False)
    instagram = forms.CharField(max_length=500, required=False)
    address = forms.CharField(max_length=500, required=False)
    emergency_contact = forms.CharField(max_length=500, required=False)
    emergency_contact_phone = forms.CharField(max_length=500, required=False)
    hide_from_leaderboard = forms.BooleanField(required=False)

    USER_FIELDS = ("first_name", "last_name", "phone_number")
    PROFILE_FIELDS = (
        "birthdate",
        "height",
        "profession",
        "instagram",
        "address",
        "emergency_contact",
        "emergency_contact_phone",
        "hide_from_leaderboard",
    )

    def clean_phone_number(self):
        # phone_number is unique on User: without this the save blows up with an
        # IntegrityError instead of saying what the problem is.
        phone = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone:
            return ""
        clash = User.objects.filter(phone_number=phone)
        if self.instance_pk:
            clash = clash.exclude(pk=self.instance_pk)
        if clash.exists():
            raise forms.ValidationError("Ese teléfono ya está en otra cuenta.")
        return phone

    def __init__(self, *args, instance_pk=None, **kwargs):
        self.instance_pk = instance_pk
        super().__init__(*args, **kwargs)

    def save(self, user):
        data = self.cleaned_data
        for field in self.USER_FIELDS:
            setattr(user, field, data.get(field) or "")
        user.save(update_fields=list(self.USER_FIELDS))

        profile, _ = Profile.objects.get_or_create(user=user)
        for field in self.PROFILE_FIELDS:
            setattr(profile, field, data.get(field))
        profile.save(update_fields=list(self.PROFILE_FIELDS))
        return user


class ClassForm(forms.Form):
    """The class record: the schedule and its training type."""

    name = forms.CharField(max_length=255)
    is_group = forms.BooleanField(required=False)
    day = forms.ChoiceField(choices=Classes.DaysChoices.choices)
    hour_init = forms.TimeField()
    hour_end = forms.TimeField()
    photo = forms.ImageField(required=False)

    def clean(self):
        data = super().clean()
        inicio, fin = data.get("hour_init"), data.get("hour_end")
        if inicio and fin and fin <= inicio:
            raise forms.ValidationError("La hora de fin tiene que ser posterior al inicio.")
        return data

    def save(self, klass):
        data = self.cleaned_data
        kind = klass.training_type
        kind.name = data["name"]
        kind.is_group = data["is_group"]
        if data.get("photo"):
            kind.photo = data["photo"]
        kind.save()

        klass.day = data["day"]
        klass.hour_init = data["hour_init"]
        klass.hour_end = data["hour_end"]
        # day+hours+type is unique: if it already exists the save raises
        # IntegrityError, so we warn before getting there.
        clash = (
            Classes.objects.filter(
                day=klass.day,
                hour_init=klass.hour_init,
                hour_end=klass.hour_end,
                training_type=kind,
            )
            .exclude(pk=klass.pk)
            .exists()
        )
        if clash:
            raise forms.ValidationError("Ya existe ese horario para esta clase.")
        klass.save()
        return klass


class VideoForm(forms.ModelForm):
    """A library video.

    The source decides which field is required: a link with no URL, or an upload
    with no file, is a video nobody can play."""

    class Meta:
        model = Video
        fields = [
            "name", "description", "source", "url", "file", "thumbnail",
            "duration_seconds", "training_type", "level", "is_published",
        ]

    def clean(self):
        data = super().clean()
        fuente = data.get("source")
        if fuente == Video.Source.URL and not data.get("url"):
            self.add_error("url", "Un video de enlace necesita la URL.")
        if fuente == Video.Source.UPLOAD and not (data.get("file") or self.instance.file):
            self.add_error("file", "Un video subido necesita el archivo.")
        return data


class VideoPackageForm(forms.ModelForm):
    """Un paquete de videos."""

    class Meta:
        model = VideoPackage
        fields = ["name", "description", "cover", "kind", "is_published"]


class AssignmentForm(forms.Form):
    """Who a package is assigned to.

    One target per submission --members, a plan, or everyone-- but the member
    target accepts several: assigning a routine to six people should not mean six
    trips through the form."""

    target = forms.ChoiceField(
        choices=[("user", "Usuarios"), ("plan", "Un plan"), ("everyone", "Todos")]
    )
    users = forms.TypedMultipleChoiceField(
        coerce=int, required=False, choices=[]
    )
    plan = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Choices come from the database, not the client: without this a
        # handcrafted POST could assign the package to a staff account.
        self.fields["users"].choices = [
            (u.pk, u.pk)
            for u in User.objects.filter(is_client=True, is_staff=False).only("pk")
        ]

    def clean(self):
        data = super().clean()
        target = data.get("target")
        if target == "user" and not data.get("users"):
            self.add_error("users", "Elegí al menos un usuario.")
        if target == "plan" and not data.get("plan"):
            self.add_error("plan", "Elegí qué plan.")
        return data

    def save(self, package):
        target = self.cleaned_data["target"]
        # get_or_create, not create: the same assignment twice would inflate
        # the reach, and the database constraint does not cover duplicates.
        if target == "user":
            return [
                PackageAssignment.objects.get_or_create(package=package, user_id=uid)[0]
                for uid in self.cleaned_data["users"]
            ]
        if target == "plan":
            return [
                PackageAssignment.objects.get_or_create(
                    package=package, plan_id=self.cleaned_data["plan"]
                )[0]
            ]
        return [
            PackageAssignment.objects.get_or_create(package=package, everyone=True)[0]
        ]

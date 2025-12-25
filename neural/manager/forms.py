"""Manager app forms."""

from django import forms
from django.contrib.auth import authenticate

from neural.users.models import User, PushNotification, Device


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
        queryset=User.objects.filter(
            is_client=True,
            devices__is_active=True
        ).distinct().order_by("first_name", "last_name"),
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

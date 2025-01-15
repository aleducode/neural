"""Users Forms"""

from django import forms
from django.contrib.auth import (
    authenticate,
)
from django.contrib.auth import forms as admin_forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from neural.users.models import Plan, User, Profile


class UserChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(admin_forms.UserCreationForm):
    error_message = admin_forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class CustomAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    email/password logins.
    """

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    error_messages = {
        "invalid_login": (
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        "inactive": "This account is inactive.",
    }

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, email=email.lower(), password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
        )


class SignUpForms(forms.Form):
    """Sign up form."""

    password = forms.CharField(
        max_length=70,
        label="",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    password_confirmation = forms.CharField(
        max_length=70,
        label="",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    first_name = forms.CharField(
        min_length=2,
        max_length=50,
        label="",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        min_length=2,
        max_length=50,
        label="",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    phone_number = forms.CharField(
        min_length=2,
        max_length=50,
        label="",
        initial="",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ejemplo +57 300 000 00 00"}
        ),
    )
    phone_prefix = forms.CharField(
        min_length=2,
        max_length=50,
        label="",
        initial="+57",
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": True}),
    )

    email = forms.CharField(
        min_length=6,
        max_length=70,
        label="",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    def clean_phone_number(self):
        """Phone number must be unique."""
        phone_number = self.cleaned_data["phone_number"]
        phone_number = f"+{self.data['phone_prefix']}{phone_number}"
        phone_number_taken = User.objects.filter(phone_number=phone_number).exists()
        if phone_number_taken:
            raise forms.ValidationError("Número de teléfono ya registrado.")
        return phone_number

    def clean_email(self):
        """Email must be unique."""
        email = self.cleaned_data["email"]
        email_taken = User.objects.filter(email=email).exists()
        if email_taken:
            raise forms.ValidationError("Email ya registrado.")
        return email

    def clean(self):
        """Veirify password confirmation match."""
        data = super().clean()
        password = data["password"]
        password_confirmation = data["password_confirmation"]

        if password != password_confirmation:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return data

    def save(self):
        """Create user and profile."""
        data = self.cleaned_data
        data.pop("password_confirmation")
        data["username"] = data["email"]
        data.pop("phone_prefix", None)
        user = User.objects.create_user(**data)
        return user


class ProfileForm(forms.Form):
    """Profile form."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    plan = forms.ModelChoiceField(
        queryset=Plan.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    birthdate = forms.DateField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "type": "date", "value": "2000-01-01"}
        )
    )
    address = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    emergency_contact = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre de contacto de emergencia",
            }
        )
    )
    emergency_contact_phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Número de contacto de emergencia",
            }
        )
    )
    profession = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    instagram = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def save(self):
        """Update user's profile data."""
        profle, _ = Profile.objects.update_or_create(
            user=self.user, defaults=self.cleaned_data
        )
        return profle

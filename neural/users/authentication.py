"""User Authentication utils."""

import logging

# Django
from django import forms
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.contrib.auth.forms import SetPasswordForm

logger = logging.getLogger(__name__)


class CustomSetPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": "Las contraseñas no coinciden",
    }
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        error_messages={
            "required": "Este campo es requerido",
        },
    )
    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        error_messages={
            "required": "Este campo es requerido",
        },
    )


class PasswordResetConfirmViewCustom(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    post_reset_login = True
    success_url = reverse_lazy("users:login")
    post_reset_login_backend = "django.contrib.auth.backends.ModelBackend"

    def form_valid(self, form):
        response = super().form_valid(
            form
        )  # Let the parent class handle the form validation
        user = form.save()
        # Manually set the backend attribute if not already set
        if not hasattr(user, "backend"):
            user.backend = "django.contrib.auth.backends.ModelBackend"
        # Log the user in
        if self.post_reset_login:
            login(self.request, user, backend=user.backend)
        return response


class PasswordResetCustomView(PasswordResetView):
    html_email_template_name = PasswordResetView.email_template_name

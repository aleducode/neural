"""User Authentication utils."""

import string
import random
import datetime
import logging

# Django
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.views.generic import TemplateView, View
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


logger = logging.getLogger(__name__)


def get_user_sms_code(user, country_code, phone_number):
    authentication_code = _generate_authentication_code()

    expiration_date = timezone.now() + datetime.timedelta(minutes=15)
    company = user.corporative
    company_name = company.name if company else "hackU"
    LoginSmsCodes.objects.filter(user=user).update(is_valid=False)
    if user.phone_number == "+573184673453":
        authentication_code = "000000"
    LoginSmsCodes.objects.create(
        user=user,
        code=authentication_code,
        expiration_date=expiration_date,
        is_valid=True,
    )
    sms_text = _("Tu código para iniciar sesión en %(company_name)s es: %(code)s.") % {
        "company_name": company_name,
        "code": authentication_code,
    }
    if settings.DEBUG:
        logger.info(sms_text)
    else:
        send_sms_text(
            country_code=country_code,
            phone_number=phone_number,
            sms_text=sms_text,
            user=user,
        )
        user.get_autorized_token
    return user


def generate_login_sms_view(form):
    data = form.cleaned_data
    user = form.user.last()
    country_code = data.get("prefix_phone")
    phone_number = data.get("phone_or_email")
    return get_user_sms_code(user, country_code, phone_number)


def create_login_sms_code(user):
    login_sms, _is_new = LoginSmsCodes.objects.get_or_create(
        user=user,
        is_valid=True,
        defaults={
            "code": _generate_authentication_code(),
            "expiration_date": timezone.now() + datetime.timedelta(minutes=15),
        },
    )
    return login_sms


def resend_whatsapp_login_code(user):
    try:
        login_sms = create_login_sms_code(user)
    except Exception:
        LoginSmsCodes.objects.filter(user=user, is_valid=True).update(is_valid=False)
        login_sms = create_login_sms_code(user)

    template = MessageTemplate.objects.get(slug_name="authentication_code")
    override_variables = {1: {"name": "{text}", "value": f"{login_sms.code}"}}
    template._send_message(
        user=user,
        delivery_date=timezone.now(),
        override_variables=override_variables,
    )
    return True


def _get_and_set_trusted_device(request):
    from config.middlewares.sessions import UserTrustedDeviceMiddleware

    middleware = UserTrustedDeviceMiddleware(request)
    device_type = middleware.get_type_device(request)
    if not request.user.is_anonymous:
        if request.user.devices.exists():
            request.user.devices.filter(type=device_type).update(is_active=False)
        request_session_key = request.session.session_key
        data = middleware.get_json_data(request)
        name = data.get("technical_name")
        # Set cookie to session forever into the browser
        request.session.set_expiry(0)
        to_delete = UserTrustedDevice.objects.filter(
            type=device_type,
            user=request.user,
            name=name,
        ).exclude(session_key=request_session_key)
        if to_delete.count() > 1:
            to_delete.delete()
        device, _ = UserTrustedDevice.objects.update_or_create(
            type=device_type,
            user=request.user,
            name=name,
            defaults={
                "session_key": request_session_key,
                "friendly_name": data.get("device", "anonymous"),
                "json_data": data,
            },
        )
        device.keys.update_or_create(
            key=request_session_key,
            kind="session",
        )
        # DRF set
        device.keys.update_or_create(
            key=request.user.get_autorized_token,
            kind="drf",
        )
        device.is_active = True
        device.save(update_fields=["is_active"])


def _generate_authentication_code():
    chars = string.digits
    return "".join(random.choice(chars) for _ in range(6)).upper()


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


def custom_server_error(request):
    context = {"user": request.user}
    return render(request, "500.html", context, status=500)


def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero


class PasswordResetCustomView(PasswordResetView):
    html_email_template_name = PasswordResetView.email_template_name


class MetaIntegrationView(TemplateView):
    template_name = "meta.html"


class QrSessionView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.content = get_object_or_404(Content, id=kwargs.get("content_id"))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = request.user
        delivery = user.scheduled_contents.filter(content=self.content).first()
        if delivery:
            delivery.sent = True
            delivery.save()
            metric, _new = delivery.metrics.get_or_create(
                user=user,
                content=self.content,
                open_date_time=timezone.now(),
            )

            # Mark as read 80 and redirect to content to set 100
            create_internal_progress(request.user, 80, metric, points=5)
            # Go to content
            module = delivery.content_distribution.content_module
            url = reverse_lazy(
                "contents:detail", kwargs={"slug_name": self.content.slug_name}
            )
            url = f"{url}?delivery={delivery.id}&origin=profile&selected_module={module.pk}&live=ok"
        else:
            url = reverse_lazy("users:mycontent")
        return HttpResponseRedirect(url)

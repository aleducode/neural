"""Users views."""

import hashlib
import random
import string

from datetime import timedelta

# Django
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView, View
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

# Forms
from neural.users.forms import SignUpForms
from neural.users.forms import CustomAuthenticationForm, ProfileForm

# Models
from neural.training.models import UserTraining
from neural.users.models import User, NeuralPlan


class LoginView(auth_views.LoginView):
    """Login view."""

    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    """logout view."""

    pass


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_date = timezone.localdate()
        user = self.request.user
        last_training = (
            UserTraining.objects.filter(
                user=self.request.user,
                slot__date__gte=now_date,
                status=UserTraining.Status.CONFIRMED,
            )
            .select_related("slot__class_trainging__training_type")
            .last()
        )
        profile = user.profile if hasattr(user, "profile") else None
        resume_year = user.rankings.exists()
        context["resume_year"] = resume_year
        context["profile"] = profile
        if last_training:
            day = last_training.slot.date
            if day == now_date:
                day_name = "hoy"
            elif day == now_date + timedelta(days=1):
                day_name = "Mañana"
            else:
                translate_day = _(day.strftime("%A"))
                day_name = f"El {translate_day}"
            hour = last_training.slot.class_trainging.hour_init.strftime("%I:%M %p")
            training_name = last_training.slot.class_trainging.training_type.name
            context["last_training"] = {
                "day": day_name,
                "hour": hour,
                "message": f"Recuerda:  Tu proximo entrenamiento es {training_name} {day_name} a las {hour}",
            }
        # Strike logic
        week_number = now_date.isocalendar()[1]
        year = now_date.year
        strike = user.strikes.filter(is_current=True).first()
        context["strike"] = strike
        stats = user.stats.filter(year=year, week=week_number).first()
        context["stats"] = stats
        return context


class PendingView(LoginRequiredMixin, TemplateView):
    template_name = "users/pending_membership.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated:
            if user.is_verified:
                return HttpResponseRedirect(reverse_lazy("users:index"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        phone_neural = f"57{settings.NEURAL_PHONE}"
        message = f"https://wa.me/{phone_neural}?text=Hola+Neural+estoy+listo+para+iniciar+mis+entrenos+mi+nombre+es+{user.first_name}+{user.last_name}."
        context["message"] = message
        return context


class SignUpView(FormView):
    template_name = "users/register.html"
    form_class = SignUpForms

    success_url = reverse_lazy("users:pending")

    def form_valid(self, form):
        user = form.save()
        # Force login
        login(self.request, user)
        return super().form_valid(form)


class SwitchUserView(LoginRequiredMixin, View):
    template_name = "users/index.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse_lazy("users:index"))

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        user_to_switch = User.objects.get(pk=pk)
        login(self.request, user_to_switch)
        return HttpResponseRedirect(reverse_lazy("users:index"))


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "users/profile.html"
    form_class = ProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, "Perfil actualizado correctamente")
        return reverse_lazy("users:profile")


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/my-profile.html"


class MembershipView(LoginRequiredMixin, TemplateView):
    template_name = "users/membership.html"

    def get(self, request, *args, **kwargs):
        order_id = request.GET.get("bold-order-id")
        payment_status = request.GET.get("bold-tx-status")
        if order_id and payment_status:
            if payment_status == "approved":
                active_payment = request.user.payments.filter(
                    reference=order_id,
                    is_paid=False,
                ).last()
                if active_payment:
                    active_payment.apply_membership()
                messages.success(request, "Pago exitoso y membresía activada")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        active_membership = user.memberships.filter(is_active=True).first()
        if not active_membership:
            last_membership = user.memberships.last()
            membership = last_membership
        else:
            membership = active_membership
        context["membership"] = membership

        # Price logic
        random_transaction_id = "".join(
            random.choices(string.ascii_letters + string.digits, k=7)
        )
        if not membership:
            plan = NeuralPlan.objects.filter(name="Mensualidad").first()
        else:
            plan = membership.plan
        context["plan"] = plan
        user.payments.create(
            reference=random_transaction_id,
            amount=plan.raw_price,
            plan=plan,
        )
        context["random_transaction_id"] = random_transaction_id
        secret_key = settings.BOLD_SECRET
        cadena_concatenada = f"{random_transaction_id}{plan.raw_price}COP{secret_key}"

        # Crear un objeto hash SHA-256
        m = hashlib.sha256()
        m.update(cadena_concatenada.encode())
        hash_hex = m.hexdigest()
        context["hash_hex"] = hash_hex
        if not settings.DEBUG:
            context["membership_link"] = reverse_lazy("users:membership")
        else:
            context["membership_link"] = "https://app.neural.com.co" + reverse_lazy(
                "users:membership"
            )
        return context

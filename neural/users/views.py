"""Users views."""

import hashlib
import random
import string

from datetime import timedelta

# Django
from django.contrib.auth import login
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum, Count, Max
from django.db.models.functions import ExtractMonth, ExtractWeekDay, ExtractHour
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
            .select_related("slot__class_training__training_type")
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
            hour = last_training.slot.class_training.hour_init.strftime("%I:%M %p")
            training_name = last_training.slot.class_training.training_type.name
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
        # Membership
        membership = user.memberships.filter(is_active=True).first()
        context["membership"] = membership
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
        context["membership_link"] = "https://app.neural.com.co" + reverse_lazy(
            "users:membership"
        )
        return context


class YearInReviewView(LoginRequiredMixin, TemplateView):
    """Year in Review - Spotify Wrapped style stats."""

    template_name = "users/year_in_review.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        year = self.kwargs.get("year", timezone.localdate().year)

        # Basic aggregated stats from UserStats
        yearly_stats = user.stats.filter(year=year).aggregate(
            total_trainings=Sum("trainings"),
            total_calories=Sum("calories"),
            total_hours=Sum("hours"),
            active_weeks=Count("id"),
        )

        context["year"] = year
        context["total_trainings"] = yearly_stats["total_trainings"] or 0
        context["total_calories"] = yearly_stats["total_calories"] or 0
        context["total_hours"] = yearly_stats["total_hours"] or 0
        context["active_weeks"] = yearly_stats["active_weeks"] or 0

        # Get all confirmed trainings for the year
        user_trainings = UserTraining.objects.filter(
            user=user,
            slot__date__year=year,
            status__in=[UserTraining.Status.CONFIRMED, UserTraining.Status.DONE],
        ).select_related("slot__class_training__training_type")

        # Monthly breakdown for chart
        monthly_data = (
            user_trainings.annotate(month=ExtractMonth("slot__date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        months_dict = {m["month"]: m["count"] for m in monthly_data}
        month_names = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
        context["monthly_labels"] = month_names
        context["monthly_data"] = [months_dict.get(i, 0) for i in range(1, 13)]

        # Best month
        if months_dict:
            best_month_num = max(months_dict, key=months_dict.get)
            context["best_month"] = month_names[best_month_num - 1]
            context["best_month_trainings"] = months_dict[best_month_num]
        else:
            context["best_month"] = None
            context["best_month_trainings"] = 0

        # Favorite training type
        training_types = (
            user_trainings.values("slot__class_training__training_type__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        if training_types:
            context["favorite_training_type"] = training_types[0][
                "slot__class_training__training_type__name"
            ]
            context["favorite_training_count"] = training_types[0]["count"]
        else:
            context["favorite_training_type"] = None
            context["favorite_training_count"] = 0

        # Favorite day of week
        day_names = {
            1: "Domingo",
            2: "Lunes",
            3: "Martes",
            4: "Miércoles",
            5: "Jueves",
            6: "Viernes",
            7: "Sábado",
        }
        weekday_data = (
            user_trainings.annotate(weekday=ExtractWeekDay("slot__date"))
            .values("weekday")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        if weekday_data:
            favorite_day_num = weekday_data[0]["weekday"]
            context["favorite_day"] = day_names.get(favorite_day_num, "")
            context["favorite_day_count"] = weekday_data[0]["count"]
        else:
            context["favorite_day"] = None
            context["favorite_day_count"] = 0

        # Weekday distribution for chart
        weekday_labels = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
        weekday_dict = {w["weekday"]: w["count"] for w in weekday_data}
        context["weekday_labels"] = weekday_labels
        context["weekday_data"] = [weekday_dict.get(i, 0) for i in range(1, 8)]

        # Favorite time slot
        time_data = (
            user_trainings.annotate(hour=ExtractHour("slot__class_training__hour_init"))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        if time_data:
            favorite_hour = time_data[0]["hour"]
            if favorite_hour < 12:
                context["favorite_time"] = "Mañana"
                context["favorite_time_emoji"] = "🌅"
            elif favorite_hour < 18:
                context["favorite_time"] = "Tarde"
                context["favorite_time_emoji"] = "☀️"
            else:
                context["favorite_time"] = "Noche"
                context["favorite_time_emoji"] = "🌙"
            context["favorite_time_count"] = time_data[0]["count"]
        else:
            context["favorite_time"] = None
            context["favorite_time_emoji"] = ""
            context["favorite_time_count"] = 0

        # Best streak
        best_strike = user.strikes.aggregate(max_weeks=Max("weeks"))
        context["best_streak"] = best_strike["max_weeks"] or 0

        # Current streak
        current_strike = user.strikes.filter(is_current=True).first()
        context["current_streak"] = current_strike.weeks if current_strike else 0

        # Ranking
        ranking = user.rankings.first()
        context["ranking_position"] = ranking.position if ranking else None
        context["ranking_total"] = User.objects.filter(
            is_verified=True, is_client=True
        ).count()

        # Fun metrics
        # Average trainings per week
        if context["active_weeks"] > 0:
            context["avg_trainings_per_week"] = round(
                context["total_trainings"] / context["active_weeks"], 1
            )
        else:
            context["avg_trainings_per_week"] = 0

        # Equivalent metrics for fun
        # Assuming 400 calories per training
        context["pizzas_burned"] = round(context["total_calories"] / 2000, 1)
        context["marathons_equivalent"] = round(
            context["total_calories"] / 2600, 1
        )  # ~2600 cal per marathon

        # Days since first training
        first_training = user_trainings.order_by("slot__date").first()
        if first_training:
            days_as_member = (timezone.localdate() - first_training.slot.date).days
            context["days_as_member"] = days_as_member
        else:
            context["days_as_member"] = 0

        # Percentage of year trained
        days_in_year = 366 if year % 4 == 0 else 365
        context["percentage_of_year"] = round(
            (context["total_trainings"] / days_in_year) * 100, 1
        )

        return context

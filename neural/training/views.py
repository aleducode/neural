"""Training views."""

# Django
from django.contrib import messages
from datetime import timedelta
from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils.translation import activate

from django.views.generic import TemplateView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

# Models
from neural.training.models import Slot, UserTraining
from datetime import datetime


class ScheduleV1View(LoginRequiredMixin, TemplateView):
    template_name = "training/schedule-v1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = []
        now = timezone.localdate()
        # Activate language translation
        activate("es")
        custom_filters = {}
        if self.request.GET.get("type"):
            custom_filters["class_training__training_type__slug_name"] = (
                self.request.GET.get("type")
            )
        if custom_filters:
            slots = (
                Slot.objects.filter(
                    **custom_filters, date__range=[now, now + timedelta(days=7)]
                )
                .values_list("date", flat=True)
                .order_by("-date")
                .distinct()
            )
            for slot in slots:
                day = slot
                day_name = _(day.strftime("%A"))
                days.append({"date": f"{day}", "day": day_name})
            # Sort by date
            days = sorted(days, key=lambda x: x["date"])
        else:
            for i in range(0, 7):
                day = now + timedelta(days=i)
                if day.isoweekday() != 8:
                    day_name = _(day.strftime("%A"))
                    days.append({"date": f"{day}", "day": day_name})
        context["days"] = days
        return context


class TrainingByDateView(LoginRequiredMixin, TemplateView):
    template_name = "training/sessions.html"
    format_date = "%Y-%m-%d"

    def dispatch(self, request, *args, **kwargs):
        self.date = kwargs.get("date")
        self.date_obj = datetime.strptime(self.date, self.format_date)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pemission_to_schedule = True
        now = timezone.localtime()
        now_date = timezone.localtime().strftime(self.format_date)
        context = super().get_context_data(**kwargs)
        filter_dict = {
            "date": self.date_obj,
        }
        if self.request.GET.get("type"):
            filter_dict["class_training__training_type__slug_name"] = (
                self.request.GET.get("type")
            )
        # Permissions
        if UserTraining.objects.filter(
            slot__date=self.date,
            user=self.request.user,
            status=UserTraining.Status.CONFIRMED,
        ).exists():
            pemission_to_schedule = False
            link = reverse_lazy("training:my_schedule")
            messages.warning(
                self.request,
                f'Ya reservaste para este día si quieres modificarlo cancela tu clase activa <a href="{link}">aquí</a>',
                extra_tags="safe",
            )
            context["already_scheduled"] = True
        if self.date == now_date:
            filter_dict["class_training__hour_init__gte"] = now
        context["sessions"] = (
            Slot.objects.filter(**filter_dict)
            .select_related(
                "class_training",
                "class_training__training_type",
            )
            .order_by("class_training__hour_init")
        )
        activate("es")
        context["name_day"] = _(self.date_obj.strftime("%A"))
        context["date"] = self.date
        context["pemission_to_schedule"] = pemission_to_schedule
        return context


class TrainingSlotView(LoginRequiredMixin, DetailView):
    template_name = "training/seats.html"
    queryset = Slot.objects.all()
    success_url = reverse_lazy("training:schedule-done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = self.get_object()
        context["slot"] = slot
        slot_date = slot.date.strftime("%Y-%m-%d")
        context["date"] = slot_date
        return context

    def _update_stats(self, user, slot):
        year = timezone.now().year
        slot_week_number = slot.date.isocalendar()[1]
        try:
            stats, created = user.stats.get_or_create(
                year=year,
                week=slot_week_number,
            )
        except IntegrityError:
            # Race condition: another request created the record first
            stats = user.stats.get(year=year, week=slot_week_number)
        # Use F() expressions for atomic updates to avoid race conditions
        user.stats.filter(pk=stats.pk).update(
            trainings=F("trainings") + 1,
            calories=F("calories") + 400,
            hours=F("hours") + 1,
        )

    def post(self, request, *args, **kwargs):
        # Create User training session
        user = self.request.user
        slot = self.get_object()
        self._update_stats(user, slot)
        # Get week day of the slot
        slot_week_day = slot.date.isocalendar()[1]
        # Check streak
        streak = user.strikes.filter(is_current=True).first()
        if streak:
            # Different to this week day
            if streak.last_week != int(slot_week_day):
                # Add a strike
                streak.weeks += 1
                streak.last_week = int(slot_week_day)
                streak.save()
        else:
            # Create a new strike
            user.strikes.create(weeks=1, last_week=int(slot_week_day), is_current=True)
        # Check again spaces
        if not slot.available_places:
            messages.error(
                self.request,
                "Este espacio de entreno se ha llenado, intenta seleccionando otro horario.",
            )
            return render(
                self.request,
                self.template_name,
                {
                    "slot": slot,
                },
            )
        schedule, _ = UserTraining.objects.update_or_create(
            slot=slot, user=self.request.user, defaults={"status": "CONFIRMED"}
        )
        return HttpResponseRedirect(
            reverse_lazy("training:schedule-done", kwargs={"pk": schedule.pk})
        )


class ScheduleDoneView(LoginRequiredMixin, DetailView):
    template_name = "training/schedule-done.html"
    queryset = UserTraining.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_session = self.get_object()
        date = training_session.slot.date
        init_hour = training_session.slot.class_training.hour_init
        end_hour = training_session.slot.class_training.hour_end
        context["date"] = date
        context["init_hour"] = init_hour
        context["end_hour"] = end_hour
        return context


class MyScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "training/my_schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.localtime()
        context["user_slots"] = (
            UserTraining.objects.filter(
                user=self.request.user,
                slot__date__gte=now,
                status=UserTraining.Status.CONFIRMED,
            )
            .order_by("slot__date")
            .select_related(
                "user",
                "slot",
                "slot__class_training",
                "slot__class_training__training_type",
            )[:7]
        )
        return context

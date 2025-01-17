"""Training views."""

import calendar

# Django
from django.contrib import messages
from django.db.models import Count
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from django.views.generic import TemplateView, FormView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

# Models
from neural.training.models import Slot, UserTraining, Classes, TrainingType
from neural.users.models import Ranking
from datetime import datetime
from neural.training.forms import ClassesForm


class ScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "training/schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.localtime()
        context["date"] = now
        return context


class ScheduleV1View(LoginRequiredMixin, TemplateView):
    template_name = "training/schedule-v1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = []
        now = timezone.localdate()
        custom_filters = {}
        if self.request.GET.get("is_group"):
            custom_filters["class_trainging__training_type__is_group"] = True
        if self.request.GET.get("type"):
            custom_filters["class_trainging__training_type__slug_name"] = (
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
            "class_trainging__training_type__is_group": self.request.GET.get(
                "is_group", False
            ),
        }
        if self.request.GET.get("type"):
            filter_dict["class_trainging__training_type__slug_name"] = (
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
            messages.error(
                self.request,
                f'Ya reservaste para este día si quieres modificarlo cancela tu clase activa <a href="{link}">aquí</a>',
                extra_tags="safe",
            )
        if self.date == now_date:
            filter_dict["class_trainging__hour_init__gte"] = now
        base_filter = Slot.objects.filter(**filter_dict)
        context["sessions"] = base_filter.order_by("class_trainging__hour_init")
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
        return context

    def post(self, request, *args, **kwargs):
        # Create User training session
        slot = self.get_object()
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
        init_hour = training_session.slot.class_trainging.hour_init
        end_hour = training_session.slot.class_trainging.hour_end
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
                "slot__class_trainging",
                "slot__class_trainging__training_type",
            )[:7]
        )
        return context


class InfoView(LoginRequiredMixin, TemplateView):
    template_name = "training/info.html"


class ResumeYear(LoginRequiredMixin, TemplateView):
    template_name = "training/resume.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        years_in_the_app = timezone.localdate() - self.request.user.created.date()
        context["years_in_the_app"] = years_in_the_app.days // 365
        ranking = self.request.user.rankings.last()
        top_10 = Ranking.objects.all().order_by("position").select_related("user")[:10]
        total_ranking = Ranking.objects.count()
        context["total_ranking"] = total_ranking
        context["top_10"] = top_10
        context["ranking"] = ranking
        now = timezone.localtime()
        trainings = UserTraining.objects.filter(
            user=self.request.user,
            slot__date__year=now.year,
            status=UserTraining.Status.CONFIRMED,
        ).distinct()
        cancelled_trainings = UserTraining.objects.filter(
            user=self.request.user,
            slot__date__year=now.year,
            status=UserTraining.Status.CANCELLED,
        ).distinct()
        if trainings.count() == 0:
            return context
        context["trainings"] = trainings.count()
        context["reaction"] = "🤩" if trainings.count() >= 20 else "🤟"

        # Day selected
        best_day = (
            trainings.values("slot__date__week_day")
            .annotate(total=Count("slot__date__week_day"))
            .order_by("-total")
            .first()
        )
        context["best_day_name"] = (
            _(calendar.day_name[best_day["slot__date__week_day"] - 1])
            if best_day
            else None
        )

        # Best training
        best_train = (
            trainings.values("slot__class_trainging__training_type")
            .annotate(total=Count("slot__class_trainging__training_type"))
            .order_by("-total")
            .first()
        )
        if best_train:
            context["best_train"] = TrainingType.objects.get(
                pk=best_train["slot__class_trainging__training_type"]
            ).name
        # Best train hours
        best_train_hour = (
            trainings.values("slot__class_trainging__hour_init")
            .annotate(total=Count("slot__class_trainging__hour_init"))
            .exclude(slot__class_trainging__hour_init="05:00")
            .order_by("-total")
            .first()
        )
        context["best_train_hour"] = (
            best_train_hour["slot__class_trainging__hour_init"]
            if best_train_hour
            else None
        )

        array_per_month = (
            trainings.values("created__month")
            .annotate(total=Count("created__month"))
            .order_by("created__month")
            .distinct()
        )
        final_array = []
        for date in range(1, 13):
            if not array_per_month.filter(created__month=date).exists():
                final_array.append(0)
            else:
                final_array.append(array_per_month.get(created__month=date)["total"])
        context["array_per_month"] = final_array
        context["best_month"] = max(final_array)
        month = final_array.index(context["best_month"]) + 1
        context["best_month_name"] = _(calendar.month_name[month])

        # Worst month
        context["worst_month"] = min(final_array)
        month = final_array.index(context["worst_month"]) + 1
        context["worst_month_name"] = _(calendar.month_name[month])
        context["cancelled_trainings"] = cancelled_trainings.count()
        return context


class ClassCalendarView(TemplateView):
    template_name = "users/class_calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["days_choices"] = Classes.DaysChoices.choices
        return context


class ClassCalendarDetailView(FormView):
    template_name = "users/class_calendar_detail.html"
    form_class = ClassesForm

    def dispatch(self, request, *args, **kwargs):
        self.day_name = self.kwargs.get("day")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        classes = Classes.objects.filter(day=self.day_name).order_by("hour_init")
        return classes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["day_classes"] = self.get_queryset()
        context["day_name"] = self.day_name
        context["training_types"] = TrainingType.objects.all()
        return context

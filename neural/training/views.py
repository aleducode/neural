"""Training views."""

# Django
from django.contrib import messages
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from django.views.generic import TemplateView, FormView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

# Models
from neural.training.models import Slot, UserTraining
from neural.training.forms import SchduleForm
from neural.utils.general import generate_calendar_google_invite
from datetime import datetime


class ScheduleView(LoginRequiredMixin, FormView):
    template_name = 'training/schedule.html'
    form_class = SchduleForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['now'] = timezone.localdate()
        return kwargs

    def form_invalid(self, form):
        for field, value in form.errors.items():
            if field not in ['__all__']:
                form.fields[field].widget.attrs['class'] = 'form-control is-invalid'
        return super().form_invalid(form)

    def form_valid(self, form):
        schedule = form.save()
        return HttpResponseRedirect(reverse_lazy('training:schedule-done', kwargs={'pk': schedule.pk}))


class ScheduleV1View(LoginRequiredMixin, TemplateView):
    template_name = 'training/schedule-v1.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = []
        now = timezone.localdate()
        for i in range(0, 3):
            day = now + timedelta(days=i)
            if day.isoweekday() != 7:
                day_name = _(day.strftime("%A"))
                days.append({
                    'date': f'{day}',
                    'day': day_name})
        context['days'] = days
        return context


class TrainingByDateView(LoginRequiredMixin, TemplateView):
    template_name = 'training/sessions.html'
    format_date = "%Y-%m-%d"

    def dispatch(self, request, *args, **kwargs):
        self.date = kwargs.get('date')
        self.date_obj = datetime.strptime(self.date, self.format_date)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pemission_to_schedule = True
        now = timezone.localtime()
        now_date = timezone.localtime().strftime(self.format_date)
        context = super().get_context_data(**kwargs)
        # Permissions
        if UserTraining.objects.filter(
            slot__date=self.date,
            user=self.request.user,
            status=UserTraining.Status.CONFIRMED
        ).exists():
            pemission_to_schedule = False
            link = reverse_lazy('training:my_schedule')
            messages.error(self.request, f'Ya reservaste para este día si quieres modificarlo cancela tu clase activa <a href="{link}">aquí</a>', extra_tags='safe')

        if self.date == now_date:
            base_filter = Slot.objects.filter(
                date=self.date,
                hour_init__gte=now,
            )
        else:
            base_filter = Slot.objects.filter(
                date=self.date,
            )
        context["sessions"] = base_filter.order_by('hour_init', 'training_type')
        context['name_day'] = _(self.date_obj.strftime("%A"))
        context['date'] = self.date
        context['pemission_to_schedule'] = pemission_to_schedule
        return context


class TrainingSlotView(LoginRequiredMixin, DetailView):
    template_name = 'training/seats.html'
    queryset = Slot.objects.all()
    success_url = reverse_lazy("training:schedule-done")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slot = self.get_object()
        context['slot'] = slot
        return context

    def post(self, request, *args, **kwargs):
        # Create User training session
        slot = self.get_object()
        # Check again spaces
        if not slot.available_places:
            messages.error(
                self.request, 'Este espacio de entreno se ha llenado, intenta seleccionando otro horario.')
            return render(
                self.request,
                self.template_name, {
                    'slot': slot,
                })

        schedule, _ = UserTraining.objects.get_or_create(
            slot=slot,
            user=self.request.user,
        )
        return HttpResponseRedirect(reverse_lazy('training:schedule-done', kwargs={'pk': schedule.pk}))


class ScheduleDoneView(LoginRequiredMixin, DetailView):
    template_name = 'training/schedule-done.html'
    queryset = UserTraining.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        training_session = self.get_object()
        name_user = self.request.user.first_name
        date = training_session.slot.date
        init_hour = training_session.slot.hour_init
        end_hour = training_session.slot.hour_end
        context["calendar_url"] = generate_calendar_google_invite(name_user, date, init_hour, end_hour)
        return context


class MyScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'training/my_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.localtime()
        context['user_slots'] = UserTraining.objects.filter(
            user=self.request.user,
            slot__date__gte=now,
            status=UserTraining.Status.CONFIRMED
        ).order_by('slot__date')[:7]
        return context


class InfoView(LoginRequiredMixin, TemplateView):
    template_name = 'training/info.html'

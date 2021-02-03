"""Training views."""

# Django
from django.contrib import messages
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, FormView, DetailView
from django.urls import reverse_lazy

# Models
from neural.training.models import Slot, UserTraining, UserTemperature
from neural.training.forms import SchduleForm, TemperatureInputForm
from neural.training.serializers import SlotModelSerializer
from neural.utils.general import generate_calendar_google_invite


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


class TemperatureView(LoginRequiredMixin, FormView):
    template_name = 'training/temperature.html'
    form_class = TemperatureInputForm
    success_url = reverse_lazy('users:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        for field, value in form.errors.items():
            if field not in ['__all__']:
                form.fields[field].widget.attrs['class'] = 'form-control is-invalid'
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Temperatura grabada correctamente')
        return super().get_success_url()
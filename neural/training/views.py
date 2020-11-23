"""Training views."""

# Django
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, FormView
from django.urls import reverse_lazy

# Models
from neural.training.models import Slot
from neural.training.forms import SchduleForm
from neural.training.serializers import SlotModelSerializer


class ScheduleView(LoginRequiredMixin, FormView):
    template_name = 'training/schedule.html'
    form_class = SchduleForm
    success_url = reverse_lazy('users:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        now = timezone.localtime()
        date = timezone.localdate()
        gap_acceptance = now + timedelta(minutes=20)
        slots = Slot.objects.filter(date=date, hour_init__gte=gap_acceptance)

        kwargs['user'] = self.request.user
        kwargs['slots'] = SlotModelSerializer(slots, many=True).data

        return kwargs
    
    def get_success_url(self):
        success_url = super().get_success_url()
        return success_url

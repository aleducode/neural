"""Users views."""
from datetime import timedelta

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
from neural.training.models import UserTraining, ImagePopUp
from neural.landing.models import HeaderLanding, MainContentHeader
from neural.users.forms import SignUpForms
from neural.users.forms import (
    CustomAuthenticationForm,
    ProfileForm
)
from neural.users.models import User


class LoginView(auth_views.LoginView):
    """Login view."""

    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    """logout view."""
    pass


class LandingView(TemplateView):
    template_name = 'landing/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_pop_up = ImagePopUp.objects.filter(is_active=True).first()
        context['header_landing'] = HeaderLanding.objects.get()
        context["main_content"] = MainContentHeader.objects.get()
        context['image_pop_up'] = image_pop_up
        return context


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        from django.contrib import messages
        context = super().get_context_data(**kwargs)
        now_date = timezone.localdate()
        user = self.request.user
        last_training = UserTraining.objects.filter(
            user=self.request.user, slot__date__gte=now_date, status=UserTraining.Status.CONFIRMED).last()
        profile = user.profile if hasattr(user, 'profile') else None
        context['profile'] = profile
        if last_training:
            day = last_training.slot.date
            if day == now_date:
                day_name = 'hoy'
            elif day == now_date + timedelta(days=1):
                day_name = 'Mañana'
            else:
                translate_day = _(day.strftime("%A"))
                day_name = f'El {translate_day}'
            hour = last_training.slot.hour_init.strftime("%I:%M %p")
            messages.warning(self.request, f'Recuerda:  Tu proximo entrenamiento es {day_name} a las {hour} !!!')
        return context


class PendingView(LoginRequiredMixin, TemplateView):
    template_name = 'users/pending_membership.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated:
            if user.is_verified:
                return HttpResponseRedirect(reverse_lazy('users:index'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        phone_neural = f'57{settings.NEURAL_PHONE}'
        message = f'https://wa.me/{phone_neural}?text=Hola+Neural+estoy+listo+para+iniciar+mis+entrenos+mi+nombre+es+{user.first_name}+{user.last_name}.'
        context['message'] = message
        return context


class SignUpView(FormView):
    template_name = 'users/register.html'
    form_class = SignUpForms

    success_url = reverse_lazy('users:pending')

    def form_valid(self, form):
        user = form.save()
        # Force login
        login(self.request, user)
        return super().form_valid(form)


class SwitchUserView(LoginRequiredMixin, View):
    template_name = 'users/index.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(reverse_lazy('users:index'))

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user_to_switch = User.objects.get(pk=pk)
        login(self.request, user_to_switch)
        return HttpResponseRedirect(reverse_lazy('users:index'))


class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'users/profile.html'
    form_class = ProfileForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        profile = user.profile if hasattr(user, 'profile') else None
        if profile:
            initial['plan'] = profile.plan
            initial['birthdate'] = profile.birthdate
            initial['address'] = profile.address
            initial['emergency_contact'] = profile.emergency_contact
            initial['emergency_contact_phone'] = profile.emergency_contact_phone
            initial['profession'] = profile.profession
            initial['instagram'] = profile.instagram
        return initial

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Perfil actualizado correctamente')
        return reverse_lazy('users:profile')

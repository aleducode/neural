"""Enterprise Clients views."""

from django.contrib.auth import login
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from neural.users.forms import (
    CustomAuthenticationForm, UserCreationForm
)
from neural.training.models import UserTraining
from neural.users.forms import SignUpForms
from django.urls import reverse_lazy



class LoginView(auth_views.LoginView):
    """Login view."""

    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    """logout view."""
    pass


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

<<<<<<< HEAD
    def get_context_data(self, **kwargs):
        from django.contrib import messages
        context = super().get_context_data(**kwargs)
        now = timezone.localdate()
        today_training = UserTraining.objects.filter(user=self.request.user, slot__date=now)
        if today_training.exists():
            today_training = today_training.last()
            messages.success(self.request, f'Recuerda:  Tu proximo entrenamiento es hoy a las {today_training.slot.hour_init} !!!')
        return context



class PendingView(LoginRequiredMixin, TemplateView):
    template_name = 'users/pending_membership.html'

    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
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
=======

class SignUpView(FormView):
    template_name = 'users/signup.html'
    form_class = UserCreationForm
    fields = ['username', 'first_name', 'phone_number', 'email']
    success_url = reverse_lazy('users:login')
>>>>>>> yesid

"""Enterprise Clients views."""

from django.db.models import Sum
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, FormView
from neural.users.forms import (
    CustomAuthenticationForm,
)
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


class PendingView(LoginRequiredMixin, TemplateView):
    template_name = 'users/pending_membership.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        phone_neural = '573184673453'
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

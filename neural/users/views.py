"""Enterprise Clients views."""

from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, FormView
from neural.users.forms import (
    CustomAuthenticationForm, UserCreationForm
)
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


class SignUpView(FormView):
    template_name = 'users/signup.html'
    form_class = UserCreationForm
    fields = ['username', 'first_name', 'phone_number', 'email']
    success_url = reverse_lazy('users:login')

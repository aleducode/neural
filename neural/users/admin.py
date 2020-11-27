from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from neural.users.forms import UserChangeForm, UserCreationForm
from neural.training.models import Temperature

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("phone_number", 'is_verified')}),) + tuple(
        auth_admin.UserAdmin.fieldsets
    )
    list_display = ["email", "phone_number", 'first_name', 'last_name', "is_client", 'is_verified']
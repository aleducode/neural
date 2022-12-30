from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from neural.users.forms import UserChangeForm, UserCreationForm
from neural.users.models import User, Ranking


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("phone_number", 'is_verified')}),) + tuple(
        auth_admin.UserAdmin.fieldsets
    )
    list_display = ["email", "phone_number", 'first_name', 'last_name', "is_client", 'is_verified']


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'trainings']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user']
    ordering = ['position']

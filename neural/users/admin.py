from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _


from neural.users.forms import UserChangeForm
from neural.users.models import User, Ranking, Profile, Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    ordering = ['name']


class AdminProfileInline(admin.StackedInline):
    model = Profile
    verbose_name_plural = 'profile'
    autocomplete_fields = ['plan']


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "email", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    list_display = [
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_staff",
        "is_superuser",
    ]
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    list_filter = ["is_staff", "is_superuser"]
    ordering = ("date_joined",)
    inlines = [AdminProfileInline]


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ['user', 'position', 'trainings']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user']
    ordering = ['position']

# Django
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

# Models
from neural.users.models import (
    User,
    Ranking,
    Profile,
    Plan,
    UserMembership,
    UserStrike,
    NeuralPlan,
    UserPaymentReference,
)

# Forms
from neural.users.forms import UserChangeForm


@admin.register(UserPaymentReference)
class UserPaymentReferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "reference", "is_paid"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    list_filter = ["is_paid"]
    ordering = ["user"]


@admin.register(NeuralPlan)
class NeuralPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "duration"]
    list_editable = ["price", "duration"]
    search_fields = ["name", "description"]
    list_filter = ["name", "price", "duration"]
    readonly_fields = ["slug_name"]


@admin.register(UserStrike)
class UserStrikeAdmin(admin.ModelAdmin):
    list_display = ["user", "weeks", "is_current", "last_week"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering = ["user"]


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name", "description"]
    ordering = ["name"]


class AdminProfileInline(admin.StackedInline):
    model = Profile
    verbose_name_plural = "profile"
    autocomplete_fields = ["plan"]


class MembershipInline(admin.StackedInline):
    model = UserMembership
    ordering = ["-is_active"]
    search_fields = ["user", "membership_type"]
    extra = 0


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
                    "photo",
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
    list_filter = ["is_staff", "is_superuser", "created"]
    ordering = ("date_joined",)
    inlines = [AdminProfileInline, MembershipInline]


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ["user", "position", "trainings"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["user"]
    ordering = ["position"]

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
    Device,
    PushNotification,
    PushNotificationLog,
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


# Push Notifications Admin
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ["user", "platform", "device_id_short", "is_active", "created"]
    list_filter = ["platform", "is_active", "created"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "device_id",
        "token",
    ]
    readonly_fields = ["created", "modified"]
    ordering = ["-created"]

    @admin.display(description="Device ID")
    def device_id_short(self, obj):
        return obj.device_id[:20] + "..." if len(obj.device_id) > 20 else obj.device_id


class PushNotificationLogInline(admin.TabularInline):
    model = PushNotificationLog
    extra = 0
    readonly_fields = [
        "device",
        "expo_push_token",
        "status",
        "expo_receipt_id",
        "error_message",
        "created",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "title_short",
        "notification_type",
        "status",
        "sent_at",
        "read_at",
    ]
    list_filter = ["notification_type", "status", "created", "sent_at"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "title",
        "body",
    ]
    readonly_fields = ["sent_at", "read_at", "created", "modified"]
    ordering = ["-created"]
    inlines = [PushNotificationLogInline]
    date_hierarchy = "created"

    @admin.display(description="Título")
    def title_short(self, obj):
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        "notification",
        "device",
        "status",
        "expo_receipt_id",
        "created",
    ]
    list_filter = ["status", "created"]
    search_fields = [
        "notification__user__email",
        "notification__title",
        "expo_push_token",
        "expo_receipt_id",
    ]
    readonly_fields = [
        "notification",
        "device",
        "expo_push_token",
        "request_payload",
        "response_payload",
        "status",
        "expo_receipt_id",
        "error_message",
        "created",
        "modified",
    ]
    ordering = ["-created"]
    date_hierarchy = "created"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

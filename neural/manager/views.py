"""Manager app views."""

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    TemplateView,
    FormView,
    DetailView,
    ListView,
    UpdateView,
)

from neural.users.models import (
    User,
    Profile,
    UserMembership,
    Device,
    PushNotification,
)
from neural.services.push_notifications import (
    PushNotificationService,
    NotificationPayload,
)
from neural.manager.forms import ManagerLoginForm, SendNotificationForm, DeviceForm


class SuperStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to be superuser or staff."""

    login_url = "manager:login"

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request, "No tienes permisos para acceder a esta sección."
            )
            return redirect("manager:login")
        return super().handle_no_permission()


class ManagerLoginView(FormView):
    """Login view for manager panel."""

    template_name = "manager/login.html"
    form_class = ManagerLoginForm
    success_url = reverse_lazy("manager:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.is_staff:
                return redirect("manager:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Bienvenido, {user.first_name}!")
        return super().form_valid(form)


class ManagerLogoutView(SuperStaffRequiredMixin, TemplateView):
    """Logout view for manager panel."""

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
        return redirect("manager:login")


class DashboardView(SuperStaffRequiredMixin, TemplateView):
    """Dashboard view with general statistics."""

    template_name = "manager/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        context["total_users"] = User.objects.filter(is_client=True).count()
        context["active_memberships"] = UserMembership.objects.filter(
            is_active=True
        ).count()
        context["total_devices"] = Device.objects.filter(is_active=True).count()
        context["notifications_today"] = PushNotification.objects.filter(
            created__date=today
        ).count()

        # Recent users
        context["recent_users"] = User.objects.filter(is_client=True).order_by(
            "-date_joined"
        )[:5]

        # Recent notifications
        context["recent_notifications"] = PushNotification.objects.select_related(
            "user"
        ).order_by("-created")[:5]

        return context


class UserListView(SuperStaffRequiredMixin, ListView):
    """List view for users with search and filters."""

    template_name = "manager/users/list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            User.objects.filter(is_client=True)
            .annotate(device_count=Count("devices", filter=Q(devices__is_active=True)))
            .select_related("profile")
            .prefetch_related(
                Prefetch(
                    "memberships",
                    queryset=UserMembership.objects.filter(is_active=True),
                    to_attr="active_memberships",
                )
            )
            .order_by("-date_joined")
        )

        # Search
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )

        # Filter by membership status
        membership_filter = self.request.GET.get("membership", "")
        if membership_filter == "active":
            queryset = queryset.filter(memberships__is_active=True)
        elif membership_filter == "inactive":
            queryset = queryset.exclude(memberships__is_active=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["membership_filter"] = self.request.GET.get("membership", "")

        # Counts for filter tabs
        base_queryset = User.objects.filter(is_client=True)
        context["total_count"] = base_queryset.count()
        context["active_count"] = (
            base_queryset.filter(memberships__is_active=True).distinct().count()
        )
        context["inactive_count"] = context["total_count"] - context["active_count"]

        return context


class UserDetailView(SuperStaffRequiredMixin, DetailView):
    """Detail view for a single user."""

    template_name = "manager/users/detail.html"
    context_object_name = "user_obj"

    def get_queryset(self):
        return User.objects.filter(is_client=True).select_related("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Profile
        context["profile"], _ = Profile.objects.get_or_create(user=user)

        # Active membership
        context["membership"] = UserMembership.objects.filter(
            user=user, is_active=True
        ).first()

        # All memberships history
        context["membership_history"] = UserMembership.objects.filter(
            user=user
        ).order_by("-created")[:10]

        # Devices
        context["devices"] = Device.objects.filter(user=user).order_by("-created")

        # Notifications
        context["notifications"] = PushNotification.objects.filter(user=user).order_by(
            "-created"
        )[:20]

        return context


class NotificationListView(SuperStaffRequiredMixin, ListView):
    """List view for all notifications."""

    template_name = "manager/notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 30

    def get_queryset(self):
        queryset = PushNotification.objects.select_related("user").order_by("-created")

        # Filter by type
        notification_type = self.request.GET.get("type", "")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Filter by status
        status = self.request.GET.get("status", "")
        if status:
            queryset = queryset.filter(status=status)

        # Search by user
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(title__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["status_filter"] = self.request.GET.get("status", "")
        context["notification_types"] = PushNotification.NotificationType.choices
        context["notification_statuses"] = PushNotification.Status.choices
        return context


class SendNotificationView(SuperStaffRequiredMixin, FormView):
    """View to send push notifications."""

    template_name = "manager/notifications/send.html"
    form_class = SendNotificationForm
    success_url = reverse_lazy("manager:notification_list")

    def get_initial(self):
        initial = super().get_initial()
        user_id = self.kwargs.get("user_id")
        if user_id:
            initial["user"] = user_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.kwargs.get("user_id")
        if user_id:
            context["target_user"] = get_object_or_404(User, pk=user_id)
        return context

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        title = form.cleaned_data["title"]
        body = form.cleaned_data["body"]
        notification_type = form.cleaned_data["notification_type"]

        # Check if user has devices
        if not Device.objects.filter(user=user, is_active=True).exists():
            messages.warning(
                self.request,
                f"{user.first_name} no tiene dispositivos registrados para recibir notificaciones.",
            )
            return self.form_invalid(form)

        # Send notification
        payload = NotificationPayload(
            title=title,
            body=body,
            notification_type=notification_type,
        )

        notification = PushNotificationService.send_to_user(user, payload)

        if notification and notification.status == PushNotification.Status.SENT:
            messages.success(
                self.request,
                f"Notificación enviada correctamente a {user.first_name} {user.last_name}.",
            )
        else:
            messages.error(
                self.request,
                "Hubo un error al enviar la notificación. Revisa los logs.",
            )

        return super().form_valid(form)


class DeviceEditView(SuperStaffRequiredMixin, UpdateView):
    """View to edit a device token."""

    model = Device
    form_class = DeviceForm
    template_name = "manager/devices/edit.html"

    def get_success_url(self):
        return reverse_lazy("manager:user_detail", kwargs={"pk": self.object.user.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_obj"] = self.object.user
        return context

    def form_valid(self, form):
        messages.success(self.request, "Dispositivo actualizado correctamente.")
        return super().form_valid(form)

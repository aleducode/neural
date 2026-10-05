"""Manager app views."""

import math

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import (
    View,
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
from neural.users.display import display_name, initials
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

    # Navegacion del shell. Vive aca porque todas las pantallas del panel
    # pasan por este mixin.
    NAV = [
        ("Principal", [("Dashboard", "manager:dashboard", "dashboard", ("dashboard",))]),
        (
            "Gestión",
            [
                ("Usuarios", "manager:user_list", "users", ("user_list", "user_detail", "device_edit")),
                (
                    "Notificaciones",
                    "manager:notification_list",
                    "bell",
                    ("notification_list", "send_notification", "send_notification_user"),
                ),
            ],
        ),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current = getattr(self.request.resolver_match, "url_name", "")
        context["shell_props"] = {
            "title": self.shell_title,
            "nav": [
                {
                    "group": group,
                    "items": [
                        {
                            "label": label,
                            "url": str(reverse(route)),
                            "icon": icon,
                            "active": current in actives,
                        }
                        for label, route, icon, actives in items
                    ],
                }
                for group, items in self.NAV
            ],
            "user": {
                "name": display_name(user) or user.email,
                "initials": initials(user),
                "role": "Superusuario" if user.is_superuser else "Staff",
            },
            "logoutUrl": str(reverse("manager:logout")),
            "csrfToken": get_token(self.request),
        }
        return context

    @property
    def shell_title(self):
        return getattr(self, "page_title", "Manager")


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

    def get_context_data(self, **kwargs):
        # El login no pasa por SuperStaffRequiredMixin, asi que arma sus props
        # por su cuenta: todavia no hay sesion de la que sacar un usuario.
        context = super().get_context_data(**kwargs)
        form = context["form"]
        context["island_props"] = {
            "csrfToken": get_token(self.request),
            "errors": [str(e) for errors in form.errors.values() for e in errors],
            "email": form.data.get("email", ""),
        }
        return context

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f"Bienvenido, {user.first_name}!")
        return super().form_valid(form)


class ManagerLogoutView(SuperStaffRequiredMixin, View):
    """Cierra la sesion del panel.

    Solo POST: con GET bastaba un <img src=".../logout/"> en cualquier pagina
    ajena para cerrarle la sesion a quien la visitara.
    """

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
        return redirect("manager:login")


class DashboardView(SuperStaffRequiredMixin, TemplateView):
    """Resumen general. Es una isla."""

    template_name = "manager/dashboard.html"
    page_title = "Dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        # is_staff fuera: las cuentas internas tienen is_client=True y venian
        # inflando el total de socios.
        socios = User.objects.filter(is_client=True, is_staff=False)

        context["island_props"] = {
            "stats": [
                {
                    "label": "Total socios",
                    "value": socios.count(),
                    "description": "Usuarios registrados",
                },
                {
                    "label": "Membresías activas",
                    "value": UserMembership.objects.filter(is_active=True).count(),
                    "description": "Con membresía vigente",
                },
                {
                    "label": "Dispositivos",
                    "value": Device.objects.filter(is_active=True).count(),
                    "description": "Dispositivos activos",
                },
                {
                    "label": "Notificaciones hoy",
                    "value": PushNotification.objects.filter(created__date=today).count(),
                    "description": "Enviadas hoy",
                },
            ],
            "users": [
                {
                    "id": u.pk,
                    "name": display_name(u) or "Sin nombre",
                    "initials": initials(u),
                    "email": u.email,
                    "joined": date_format(timezone.localtime(u.date_joined), "d M Y"),
                }
                for u in socios.order_by("-date_joined")[:5]
            ],
            "notifications": [
                {
                    "id": n.pk,
                    "title": n.title,
                    "userName": display_name(n.user) or "Sin nombre",
                    "status": n.status,
                    "statusLabel": n.get_status_display(),
                }
                for n in PushNotification.objects.select_related("user").order_by("-created")[:5]
            ],
            "usersUrl": str(reverse("manager:user_list")),
            "notificationsUrl": str(reverse("manager:notification_list")),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
        }
        return context


class UserListView(SuperStaffRequiredMixin, ListView):
    """Lista de socios. La tabla es una isla de React.

    Buscar, filtrar y paginar pasaron al cliente: son ~740 filas, caben de
    sobra en una respuesta y asi cada tecla deja de recargar la pagina.
    """

    page_title = "Usuarios"

    template_name = "manager/users/list.html"
    context_object_name = "users"

    def get_queryset(self):
        return (
            # is_staff fuera: las cuentas internas tienen is_client=True y se
            # colaban como socios.
            User.objects.filter(is_client=True, is_staff=False)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["island_props"] = {
            "users": [
                {
                    "id": user.pk,
                    "name": display_name(user) or "Sin nombre",
                    "initials": initials(user),
                    "email": user.email,
                    "phone": user.phone_number or "—",
                    "joined": date_format(timezone.localtime(user.date_joined), "d M Y"),
                    "devices": user.device_count,
                    "membership": (
                        {
                            "expires": (
                                date_format(membership.expiration_date, "d M Y")
                                if membership.expiration_date
                                else None
                            )
                        }
                        if (membership := next(iter(user.active_memberships), None))
                        else None
                    ),
                }
                for user in context["users"]
            ],
            # La isla reemplaza el 0 por el id real.
            "detailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
        }
        return context


class UserDetailView(SuperStaffRequiredMixin, DetailView):
    """Detail view for a single user."""

    page_title = "Detalle de usuario"

    template_name = "manager/users/detail.html"
    context_object_name = "user_obj"

    def get_queryset(self):
        return User.objects.filter(is_client=True).select_related("profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Solo lectura: get_or_create convertia una visita en una escritura y
        # llenaba la tabla de perfiles vacios de gente que solo fuiste a mirar.
        context["profile"] = Profile.objects.filter(user=user).first()

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


class NotificationFilterMixin:
    """Filtros compartidos por la pagina y por el endpoint que la alimenta."""

    def filtered_notifications(self):
        queryset = PushNotification.objects.select_related("user").order_by("-created")

        notification_type = self.request.GET.get("type", "")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        status = self.request.GET.get("status", "")
        if status:
            queryset = queryset.filter(status=status)

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(title__icontains=search)
            )

        return queryset


class NotificationListView(SuperStaffRequiredMixin, NotificationFilterMixin, TemplateView):
    """Historial de notificaciones. La tabla es una isla.

    Son miles de filas, asi que a diferencia de la de socios esta se pagina en
    el servidor: la isla pide cada pagina a NotificationFeedView.
    """

    page_title = "Notificaciones"

    template_name = "manager/notifications/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["island_props"] = {
            "feedUrl": str(reverse("manager:notification_feed")),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
            "types": [
                {"value": v, "label": label}
                for v, label in PushNotification.NotificationType.choices
            ],
            "statuses": [
                {"value": v, "label": label}
                for v, label in PushNotification.Status.choices
            ],
        }
        return context


class NotificationFeedView(SuperStaffRequiredMixin, NotificationFilterMixin, View):
    """Pagina de notificaciones en JSON, para la isla."""

    PAGE_SIZE = 30

    def get(self, request, *args, **kwargs):
        queryset = self.filtered_notifications()
        total = queryset.count()

        try:
            page = max(1, int(request.GET.get("page", 1)))
        except (TypeError, ValueError):
            page = 1
        offset = (page - 1) * self.PAGE_SIZE

        rows = [
            {
                "id": n.pk,
                "userId": n.user_id,
                "userName": display_name(n.user) or "Sin nombre",
                "userInitials": initials(n.user),
                "title": n.title,
                "body": n.body,
                "type": n.get_notification_type_display(),
                "status": n.status,
                "statusLabel": n.get_status_display(),
                "created": date_format(timezone.localtime(n.created), "d M Y, H:i"),
            }
            for n in queryset[offset : offset + self.PAGE_SIZE]
        ]

        return JsonResponse(
            {
                "results": rows,
                "page": page,
                "pages": max(1, math.ceil(total / self.PAGE_SIZE)),
                "total": total,
            }
        )


class SendNotificationView(SuperStaffRequiredMixin, FormView):
    """View to send push notifications."""

    page_title = "Enviar notificación"

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
        target = get_object_or_404(User, pk=user_id) if user_id else None
        if target:
            context["target_user"] = target

        def card(user):
            return {
                "id": user.pk,
                "name": display_name(user) or "Sin nombre",
                "initials": initials(user),
                "email": user.email,
            }

        # Son ~140 con dispositivo activo: caben en la pagina, y asi el
        # buscador responde sin ir al servidor ni cargar jQuery y Select2.
        context["island_props"] = {
            "users": [card(u) for u in self.fields_queryset()],
            "types": [
                {"value": v, "label": label}
                for v, label in PushNotification.NotificationType.choices
            ],
            "lockedUser": card(target) if target else None,
            "defaultType": PushNotification.NotificationType.GENERAL,
            "cancelUrl": str(reverse("manager:notification_list")),
            "csrfToken": get_token(self.request),
        }
        return context

    def fields_queryset(self):
        return self.get_form().fields["user"].queryset

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

    page_title = "Dispositivo"

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

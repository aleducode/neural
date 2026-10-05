"""Manager app views."""

import math

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.formats import date_format
from django.core.exceptions import ValidationError
from neural.training.models import (
    Classes,
    PackageVideo,
    TrainingType,
    Video,
    VideoPackage,
)
from django.views.generic import (
    View,
    TemplateView,
    FormView,
    ListView,
    UpdateView,
)

from neural.users.models import (
    PushNotificationLog,
    User,
    UserMembership,
    Device,
    PushNotification,
)
from neural.services.push_notifications import (
    PushNotificationService,
    NotificationPayload,
)
from neural.users.display import display_name, initials, photo_url
from neural.manager import metrics
from neural.manager.forms import (
    VideoForm,
    VideoPackageForm,
    AssignmentForm,
    ManagerLoginForm,
    SendNotificationForm,
    DeviceForm,
    MemberProfileForm,
    ClassForm,
)


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

    # Shell navigation. It lives here because every panel screen
    # goes through this mixin.
    NAV = [
        ("Principal", [("Dashboard", "manager:dashboard", "dashboard", ("dashboard",))]),
        (
            "Gestión",
            [
                # user_list stays alive for old links, but the design's users
                # screen is member_list: they share one menu item.
                ("Usuarios", "manager:member_list", "users", ("member_list", "user_list", "user_detail", "device_edit")),
                ("Clases", "manager:class_list", "dumbbell", ("class_list", "class_detail")),
                ("Reservas", "manager:booking_list", "calendar-check", ("booking_list",)),
            ],
        ),
        (
            "Contenido",
            [
                ("Videos", "manager:video_list", "video", ("video_list",)),
                ("Paquetes", "manager:package_list", "library", ("package_list", "package_detail")),
            ],
        ),
        (
            "Operación",
            [("Calendario", "manager:calendar", "calendar", ("calendar",))],
        ),
        (
            "Finanzas",
            [
                ("Pagos", "manager:payment_list", "wallet", ("payment_list",)),
                ("Planes", "manager:plan_list", "layers", ("plan_list",)),
            ],
        ),
        (
            "Comunicación",
            [
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
        # Login does not go through SuperStaffRequiredMixin, so it builds its
        # own props: there is no session yet to read a user from.
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
    """Logs out of the panel.

    POST only: with GET, an <img src=".../logout/"> on any foreign page was enough
    to log out whoever visited it."""

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente.")
        return redirect("manager:login")


class DashboardView(SuperStaffRequiredMixin, TemplateView):
    """The business dashboard. It is an island.

    Every widget comes from a real model. What the design asked for and Neural does
    not have --trainers, payment method, class photo-- is replaced by the data that
    does exist, and the label says so. See neural/manager/metrics.py."""

    template_name = "manager/dashboard.html"
    page_title = "Dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()

        context["island_props"] = {
            "today": date_format(today, "l, j \\d\\e F \\d\\e Y").capitalize(),
            "kpis": metrics.kpis(today),
            "growth": metrics.growth(today),
            "classes": metrics.popular_classes(today),
            "revenue": metrics.revenue_by_plan(today),
            "payments": metrics.recent_payments(),
            "gaps": metrics.no_data_notice(),
            "usersUrl": str(reverse("manager:user_list")),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
            "sendUrl": str(reverse("manager:send_notification")),
        }
        return context


class UserListView(SuperStaffRequiredMixin, ListView):
    """Member list. The table is a React island.

    Search, filter and pagination moved to the client: there are ~740 rows, they
    fit comfortably in one response, and this way no keystroke reloads the page."""

    page_title = "Usuarios"

    template_name = "manager/users/list.html"
    context_object_name = "users"

    def get_queryset(self):
        return (
            # Staff excluded: internal accounts carry is_client=True and were
            # slipping in as members.
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
            # The island replaces the 0 with the real id.
            "detailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
        }
        return context


class DetailBase(SuperStaffRequiredMixin, TemplateView):
    """Base for the design's two detail screens.

    TemplateView and not View: the shell mixin builds its props in
    get_context_data, which View does not have. GET renders and POST saves on the
    same URL, so the form keeps working if the island does not mount."""

    template_name = "manager/section.html"
    island = ""

    def get_object(self):
        raise NotImplementedError

    def build_props(self, obj):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = kwargs.get("obj") or self.get_object()
        context["island"] = self.island
        context["island_props"] = {
            **self.build_props(obj),
            "errors": kwargs.get("errors") or {},
            "csrfToken": get_token(self.request),
        }
        return context


class MemberDetailView(DetailBase):
    """«41. Member - Detail 360»: everything Neural knows about a member."""

    page_title = "Detalle del usuario"
    island = "member-detail"

    def get_object(self):
        return get_object_or_404(
            User.objects.filter(is_client=True, is_staff=False), pk=self.kwargs["pk"]
        )

    def build_props(self, member):
        return {
            **metrics.member_detail(member.pk, timezone.localdate()),
            "backUrl": str(reverse("manager:member_list")),
            "sendUrl": str(
                reverse("manager:send_notification_user", kwargs={"user_id": member.pk})
            ),
            "videoPackages": metrics.member_videos(member),
            "packageDetailUrl": str(
                reverse("manager:package_detail", kwargs={"pk": 0})
            ),
        }

    def post(self, request, *args, **kwargs):
        member = self.get_object()
        form = MemberProfileForm(request.POST, instance_pk=member.pk)
        if form.is_valid():
            form.save(member)
            messages.success(request, "Ficha actualizada.")
            return redirect("manager:user_detail", pk=member.pk)
        return self.render_to_response(
            self.get_context_data(obj=member, errors=form.errors.get_json_data())
        )


class ClassDetailView(DetailBase):
    """«42. Class - Detail 360»: everything that happens in one schedule."""

    page_title = "Detalle de la clase"
    island = "class-detail"

    def get_object(self):
        return get_object_or_404(
            Classes.objects.select_related("training_type"), pk=self.kwargs["pk"]
        )

    def build_props(self, klass):
        return {
            **metrics.class_detail(klass.pk, timezone.localdate()),
            "backUrl": str(reverse("manager:class_list")),
            "calendarUrl": str(reverse("manager:calendar")),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
        }

    def post(self, request, *args, **kwargs):
        klass = self.get_object()
        form = ClassForm(request.POST, request.FILES)
        errors = None
        if form.is_valid():
            try:
                form.save(klass)
            except ValidationError as error:
                errors = {"__all__": [{"message": m} for m in error.messages]}
            else:
                messages.success(request, "Clase actualizada.")
                return redirect("manager:class_detail", pk=klass.pk)
        return self.render_to_response(
            self.get_context_data(obj=klass, errors=errors or form.errors.get_json_data())
        )


class NotificationFilterMixin:
    """Filters shared by the page and by the endpoint that feeds it."""

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
    """Notification history. The table is an island.

    There are thousands of rows, so unlike the member list this one paginates on
    the server: the island asks NotificationFeedView for each page."""

    page_title = "Notificaciones"

    template_name = "manager/notifications/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["island_props"] = {
            **metrics.notifications_page(timezone.localdate()),
            "feedUrl": str(reverse("manager:notification_feed")),
            "detailUrl": str(reverse("manager:notification_detail", kwargs={"pk": 0})),
            "sendUrl": str(reverse("manager:send_notification")),
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
    """One page of notifications as JSON, for the island."""

    PAGE_SIZE = 30

    def get(self, request, *args, **kwargs):
        queryset = self.filtered_notifications().annotate(
            attempts=Count("logs", distinct=True),
            failures=Count(
                "logs",
                filter=Q(logs__status=PushNotificationLog.Status.ERROR),
                distinct=True,
            ),
        )
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
                "userPhoto": photo_url(n.user),
                "attempts": n.attempts,
                "failures": n.failures,
            }
            for n in queryset[offset:offset + self.PAGE_SIZE]
        ]

        return JsonResponse(
            {
                "results": rows,
                "page": page,
                "pages": max(1, math.ceil(total / self.PAGE_SIZE)),
                "total": total,
            }
        )


class NotificationDetailView(SuperStaffRequiredMixin, View):
    """One delivery in detail as JSON: the modal asks for it when it opens.

    Separate from the feed because Expo's payloads are large: sending them with
    every table row would ship megabytes almost nobody looks at."""

    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse(metrics.notification_detail(self.kwargs["pk"]))
        except PushNotification.DoesNotExist:
            return JsonResponse({"error": "No existe esa notificación."}, status=404)


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

        # About 140 have an active device: they fit in the page, and the
        # search answers without a round trip or loading jQuery and Select2.
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


class SectionView(SuperStaffRequiredMixin, TemplateView):
    """Base for the section screens.

    They all share one shape in the .pen --header, four KPIs, table card-- and one
    shape here: a function in metrics.py returning the props, and an island that
    paints them."""

    island = ""
    metric = None

    def get_template_names(self):
        return ["manager/section.html"]

    def build_props(self, today):
        return self.metric(today)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context["island"] = self.island
        context["island_props"] = {
            **self.build_props(today),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
            "sendUrl": str(reverse("manager:send_notification")),
            "calendarUrl": str(reverse("manager:calendar")),
            "classDetailUrl": str(reverse("manager:class_detail", kwargs={"pk": 0})),
            "packageDetailUrl": str(reverse("manager:package_detail", kwargs={"pk": 0})),
            "csrfToken": get_token(self.request),
        }
        return context


class VideoListView(SectionView):
    """The video library."""

    page_title = "Videos"
    island = "videos"
    metric = staticmethod(metrics.videos_page)

    def build_props(self, today):
        return {
            **self.metric(today),
            "uploadUrl": str(reverse("manager:video_upload")),
            "levelChoices": [
                {"value": value, "label": label} for value, label in Video.Level.choices
            ],
            "sourceChoices": [
                {"value": value, "label": label} for value, label in Video.Source.choices
            ],
            "trainingTypes": [
                {"value": str(t.pk), "label": t.name}
                for t in TrainingType.objects.order_by("name")
            ],
        }

    def post(self, request, *args, **kwargs):
        """Create or edit a video on the same screen."""
        pk = request.POST.get("id")
        instance = Video.objects.filter(pk=pk).first() if pk else None
        form = VideoForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Video actualizado." if instance else "Video creado."
            )
            return redirect("manager:video_list")
        context = self.get_context_data()
        context["island_props"]["errors"] = form.errors.get_json_data()
        return self.render_to_response(context)


class PackageListView(SectionView):
    """The video packages."""

    page_title = "Paquetes"
    island = "packages"
    metric = staticmethod(metrics.packages_page)

    def post(self, request, *args, **kwargs):
        form = VideoPackageForm(request.POST, request.FILES)
        if form.is_valid():
            package = form.save()
            return redirect("manager:package_detail", pk=package.pk)
        context = self.get_context_data()
        context["island_props"]["errors"] = form.errors.get_json_data()
        return self.render_to_response(context)


class PackageDetailView(DetailBase):
    """The package builder: videos in order and who receives it."""

    page_title = "Paquete de videos"
    island = "package-detail"

    def get_object(self):
        return get_object_or_404(VideoPackage, pk=self.kwargs["pk"])

    def build_props(self, package):
        return {
            **metrics.package_detail(package.pk),
            "backUrl": str(reverse("manager:package_list")),
            "userDetailUrl": str(reverse("manager:user_detail", kwargs={"pk": 0})),
            "videoListUrl": str(reverse("manager:video_list")),
        }

    def post(self, request, *args, **kwargs):
        """Every builder action comes through here.

        One endpoint and an `action` field instead of six URLs: the form keeps working
        without JavaScript and there are not six routes to maintain."""
        package = self.get_object()
        action = request.POST.get("action", "save")
        errors = None

        if action == "save":
            form = VideoPackageForm(request.POST, request.FILES, instance=package)
            if form.is_valid():
                form.save()
                messages.success(request, "Paquete actualizado.")
            else:
                errors = form.errors.get_json_data()

        elif action == "add-video":
            video_id = request.POST.get("video")
            if video_id:
                last_order = package.items.aggregate(n=Max("order"))["n"] or 0
                PackageVideo.objects.get_or_create(
                    package=package,
                    video_id=video_id,
                    defaults={"order": last_order + 1},
                )

        elif action == "remove-video":
            package.items.filter(pk=request.POST.get("item")).delete()
            self._reordenar(package)

        elif action == "move-video":
            self._mover(package, request.POST.get("item"), request.POST.get("dir"))

        elif action == "assign":
            form = AssignmentForm(request.POST)
            if form.is_valid():
                form.save(package)
            else:
                errors = form.errors.get_json_data()

        elif action == "unassign":
            package.assignments.filter(pk=request.POST.get("assignment")).delete()

        if errors:
            return self.render_to_response(
                self.get_context_data(obj=package, errors=errors)
            )
        return redirect("manager:package_detail", pk=package.pk)

    @staticmethod
    def _reordenar(package):
        """Leaves the order as 1..n with no gaps after a delete or a move."""
        for position, item in enumerate(package.items.order_by("order", "id"), start=1):
            if item.order != position:
                PackageVideo.objects.filter(pk=item.pk).update(order=position)

    def _mover(self, package, item_id, direction):
        items = list(package.items.order_by("order", "id"))
        indexes = {str(i.pk): n for n, i in enumerate(items)}
        if item_id not in indexes:
            return
        current = indexes[item_id]
        target = current - 1 if direction == "up" else current + 1
        if not 0 <= target < len(items):
            return
        items[current], items[target] = items[target], items[current]
        for position, item in enumerate(items, start=1):
            PackageVideo.objects.filter(pk=item.pk).update(order=position)


class MemberListView(SectionView):
    """«14. Member - List View» with Neural's members."""

    page_title = "Usuarios"
    island = "members"
    metric = staticmethod(metrics.members_page)


class ClassListView(SectionView):
    """«19. Class - List View» sobre TrainingType + Classes."""

    page_title = "Clases"
    island = "classes"
    metric = staticmethod(metrics.classes_page)


class BookingListView(SectionView):
    """«22. Booking - List View» sobre UserTraining."""

    page_title = "Reservas"
    island = "bookings"
    metric = staticmethod(metrics.bookings_page)


class PaymentListView(SectionView):
    """«26. Transactions - List View» sobre UserPaymentReference."""

    page_title = "Pagos"
    island = "payments"
    metric = staticmethod(metrics.payments_page)


class PlanListView(SectionView):
    """The NeuralPlan catalogue, read as «30. Settings - Plan»."""

    page_title = "Planes"
    island = "plans"
    metric = staticmethod(metrics.plans_page)


class CalendarView(SectionView):
    """«23. Calendar View - Month» over the month's Slots."""

    page_title = "Calendario"
    island = "calendar"

    def build_props(self, today):
        # The month arrives via querystring so calendar navigation leaves
        # shareable URLs instead of client-only state.
        def as_int(field, low, high):
            try:
                value = int(self.request.GET.get(field, ""))
            except (TypeError, ValueError):
                return None
            return value if low <= value <= high else None

        return metrics.calendar_month(
            today, year=as_int("year", 2000, 2100), month=as_int("month", 1, 12)
        )

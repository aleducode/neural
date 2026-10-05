"""Manager app URLs."""

from django.urls import path

from neural.manager.uploads import VideoUploadView
from neural.manager.views import (
    ManagerLoginView,
    ManagerLogoutView,
    DashboardView,
    UserListView,
    MemberDetailView,
    ClassDetailView,
    NotificationListView,
    NotificationFeedView,
    NotificationDetailView,
    SendNotificationView,
    DeviceEditView,
    MemberListView,
    ClassListView,
    BookingListView,
    CalendarView,
    PaymentListView,
    PlanListView,
    VideoListView,
    PackageListView,
    PackageDetailView,
)

app_name = "manager"

urlpatterns = [
    # Authentication
    path("login/", ManagerLoginView.as_view(), name="login"),
    path("logout/", ManagerLogoutView.as_view(), name="logout"),
    # Dashboard
    path("", DashboardView.as_view(), name="dashboard"),
    # Users
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", MemberDetailView.as_view(), name="user_detail"),
    path("classes/<int:pk>/", ClassDetailView.as_view(), name="class_detail"),
    # Secciones del panel (diseno docs/design/manager.pen)
    path("members/", MemberListView.as_view(), name="member_list"),
    path("classes/", ClassListView.as_view(), name="class_list"),
    path("bookings/", BookingListView.as_view(), name="booking_list"),
    path("calendar/", CalendarView.as_view(), name="calendar"),
    path("payments/", PaymentListView.as_view(), name="payment_list"),
    path("plans/", PlanListView.as_view(), name="plan_list"),
    path("videos/", VideoListView.as_view(), name="video_list"),
    path("videos/upload/", VideoUploadView.as_view(), name="video_upload"),
    path("packages/", PackageListView.as_view(), name="package_list"),
    path("packages/<int:pk>/", PackageDetailView.as_view(), name="package_detail"),
    # Devices
    path("devices/<int:pk>/edit/", DeviceEditView.as_view(), name="device_edit"),
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    # Alimenta la isla de la tabla: son miles de filas, se paginan aca.
    path(
        "notifications/data/",
        NotificationFeedView.as_view(),
        name="notification_feed",
    ),
    path(
        "notifications/<int:pk>/data/",
        NotificationDetailView.as_view(),
        name="notification_detail",
    ),
    path(
        "notifications/send/", SendNotificationView.as_view(), name="send_notification"
    ),
    path(
        "notifications/send/<int:user_id>/",
        SendNotificationView.as_view(),
        name="send_notification_user",
    ),
]

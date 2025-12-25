"""Manager app URLs."""

from django.urls import path

from neural.manager.views import (
    ManagerLoginView,
    ManagerLogoutView,
    DashboardView,
    UserListView,
    UserDetailView,
    NotificationListView,
    SendNotificationView,
    DeviceEditView,
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
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    # Devices
    path("devices/<int:pk>/edit/", DeviceEditView.as_view(), name="device_edit"),
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path("notifications/send/", SendNotificationView.as_view(), name="send_notification"),
    path(
        "notifications/send/<int:user_id>/",
        SendNotificationView.as_view(),
        name="send_notification_user",
    ),
]

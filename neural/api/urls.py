"""URL configuration for API v1."""

from django.urls import path

from neural.api.views.auth import (
    LoginView,
    LogoutView,
    MeView,
    PasswordResetRequestView,
    RegisterView,
)
from neural.api.views.dashboard import DashboardView
from neural.api.views.membership import (
    CreatePaymentView,
    MembershipView,
    PaymentWebhookView,
    VerifyPaymentView,
)
from neural.api.views.training import (
    BookView,
    CalendarView,
    CancelView,
    MyTrainingsView,
    SlotDetailView,
    SlotsView,
    TrainingTypesView,
)
from neural.api.views.year_review import YearReviewView
from neural.api.views.devices import RegisterDeviceView, UnregisterDeviceView
from neural.api.views.profile import ProfileView, WeightListView, WeightCreateView
from neural.api.views.notifications import (
    NotificationListView,
    NotificationDetailView,
    MarkNotificationReadView,
    NotificationCountView,
    SendNotificationView,
)
from neural.api.views.community import (
    FeedView,
    PostListCreateView,
    PostDetailView,
    PostReactionView,
    PostCommentsView,
    CommentDetailView,
    UserTrainingsForPostView,
    UserPublicProfileView,
)

app_name = "api"

urlpatterns = [
    # Authentication
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path("auth/me/", MeView.as_view(), name="me"),
    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Training
    path("training/calendar/", CalendarView.as_view(), name="calendar"),
    path("training/slots/", SlotsView.as_view(), name="slots"),
    path("training/slots/<int:pk>/", SlotDetailView.as_view(), name="slot_detail"),
    path("training/book/", BookView.as_view(), name="book"),
    path("training/cancel/", CancelView.as_view(), name="cancel"),
    path("training/my-trainings/", MyTrainingsView.as_view(), name="my_trainings"),
    path("training/types/", TrainingTypesView.as_view(), name="training_types"),
    # Membership
    path("membership/", MembershipView.as_view(), name="membership"),
    path(
        "membership/create-payment/", CreatePaymentView.as_view(), name="create_payment"
    ),
    path(
        "membership/verify-payment/", VerifyPaymentView.as_view(), name="verify_payment"
    ),
    path("membership/webhook/", PaymentWebhookView.as_view(), name="payment_webhook"),
    # Year in Review
    path("year-review/", YearReviewView.as_view(), name="year_review"),
    path("year-review/<int:year>/", YearReviewView.as_view(), name="year_review_year"),
    # Devices (Push Notifications)
    path("devices/register/", RegisterDeviceView.as_view(), name="register_device"),
    path(
        "devices/unregister/", UnregisterDeviceView.as_view(), name="unregister_device"
    ),
    # Profile
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/weights/", WeightListView.as_view(), name="weight_list"),
    path("profile/weights/create/", WeightCreateView.as_view(), name="weight_create"),
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path(
        "notifications/count/",
        NotificationCountView.as_view(),
        name="notification_count",
    ),
    path(
        "notifications/read-all/",
        MarkNotificationReadView.as_view(),
        name="notification_read_all",
    ),
    path(
        "notifications/<int:pk>/",
        NotificationDetailView.as_view(),
        name="notification_detail",
    ),
    path(
        "notifications/<int:pk>/read/",
        MarkNotificationReadView.as_view(),
        name="notification_read",
    ),
    path(
        "notifications/send/", SendNotificationView.as_view(), name="notification_send"
    ),
    # Community
    path("community/feed/", FeedView.as_view(), name="community_feed"),
    path("community/posts/", PostListCreateView.as_view(), name="community_posts"),
    path(
        "community/posts/<int:pk>/",
        PostDetailView.as_view(),
        name="community_post_detail",
    ),
    path(
        "community/posts/<int:pk>/react/",
        PostReactionView.as_view(),
        name="community_post_react",
    ),
    path(
        "community/posts/<int:pk>/comments/",
        PostCommentsView.as_view(),
        name="community_post_comments",
    ),
    path(
        "community/comments/<int:pk>/",
        CommentDetailView.as_view(),
        name="community_comment_detail",
    ),
    path(
        "community/trainings/",
        UserTrainingsForPostView.as_view(),
        name="community_trainings",
    ),
    path(
        "community/users/<int:user_id>/",
        UserPublicProfileView.as_view(),
        name="community_user_profile",
    ),
]

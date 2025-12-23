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
    SlotsView,
    TrainingTypesView,
)
from neural.api.views.year_review import YearReviewView
from neural.api.views.devices import RegisterDeviceView, UnregisterDeviceView

app_name = "api"

urlpatterns = [
    # Authentication
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("auth/me/", MeView.as_view(), name="me"),

    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),

    # Training
    path("training/calendar/", CalendarView.as_view(), name="calendar"),
    path("training/slots/", SlotsView.as_view(), name="slots"),
    path("training/book/", BookView.as_view(), name="book"),
    path("training/cancel/", CancelView.as_view(), name="cancel"),
    path("training/my-trainings/", MyTrainingsView.as_view(), name="my_trainings"),
    path("training/types/", TrainingTypesView.as_view(), name="training_types"),

    # Membership
    path("membership/", MembershipView.as_view(), name="membership"),
    path("membership/create-payment/", CreatePaymentView.as_view(), name="create_payment"),
    path("membership/verify-payment/", VerifyPaymentView.as_view(), name="verify_payment"),
    path("membership/webhook/", PaymentWebhookView.as_view(), name="payment_webhook"),

    # Year in Review
    path("year-review/", YearReviewView.as_view(), name="year_review"),
    path("year-review/<int:year>/", YearReviewView.as_view(), name="year_review_year"),

    # Devices (Push Notifications)
    path("devices/register/", RegisterDeviceView.as_view(), name="register_device"),
    path("devices/unregister/", UnregisterDeviceView.as_view(), name="unregister_device"),
]

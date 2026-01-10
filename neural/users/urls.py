from django.urls import path
from neural.users import views as user_views

app_name = "users"
urlpatterns = [
    path(route="", view=user_views.IndexView.as_view(), name="index"),
    path(route="pending", view=user_views.PendingView.as_view(), name="pending"),
    path(route="signup", view=user_views.SignUpView.as_view(), name="signup"),
    path(
        route="my-profile", view=user_views.MyProfileView.as_view(), name="my_profile"
    ),
    path(
        route="membership", view=user_views.MembershipView.as_view(), name="membership"
    ),
    path(route="profile", view=user_views.ProfileView.as_view(), name="profile"),
    path(route="login/", view=user_views.LoginView.as_view(), name="login"),
    path(route="logout/", view=user_views.LogoutView.as_view(), name="logout"),
    path(
        route="switch-user/<int:pk>/",
        view=user_views.SwitchUserView.as_view(),
        name="switch_user",
    ),
    path(
        route="year-in-review/",
        view=user_views.YearInReviewView.as_view(),
        name="year_in_review",
    ),
    path(
        route="year-in-review/<int:year>/",
        view=user_views.YearInReviewView.as_view(),
        name="year_in_review_year",
    ),
    # Account deletion routes (for Google Play compliance)
    path(
        route="account-deletion-info/",
        view=user_views.AccountDeletionInfoView.as_view(),
        name="account_deletion_info",
    ),
    path(
        route="account-deletion/",
        view=user_views.AccountDeletionView.as_view(),
        name="account_deletion",
    ),
    # Data deletion routes (for Google Play compliance)
    path(
        route="data-deletion-info/",
        view=user_views.DataDeletionInfoView.as_view(),
        name="data_deletion_info",
    ),
    path(
        route="data-deletion/",
        view=user_views.DataDeletionView.as_view(),
        name="data_deletion",
    ),
]

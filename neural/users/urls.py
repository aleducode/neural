from django.urls import path
from neural.users import views as user_views

app_name = "users"
urlpatterns = [
    path(route="", view=user_views.IndexView.as_view(), name="index"),
    path(route="pending", view=user_views.PendingView.as_view(), name="pending"),
    path(route="signup", view=user_views.SignUpView.as_view(), name="signup"),
    path(route="profile", view=user_views.ProfileView.as_view(), name="profile"),
    path(route="login/", view=user_views.LoginView.as_view(), name="login"),
    path(route="logout/", view=user_views.LogoutView.as_view(), name="logout"),
    path(
        route="switch-user/<int:pk>/",
        view=user_views.SwitchUserView.as_view(),
        name="switch_user",
    ),
]

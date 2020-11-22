from django.urls import path
from neural.users import views as user_views

app_name = "users"
urlpatterns = [
    path(
        route="",
        view=user_views.IndexView.as_view(),
        name='index'
    ),
    path(
        route='login/',
        view=user_views.LoginView.as_view(),
        name='login'
    ),
    path(
        route='logout/',
        view=user_views.LogoutView.as_view(),
        name='logout'
    ),
]

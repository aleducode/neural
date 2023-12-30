from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include


from neural.training import views as training_views
from neural.training import api as api_views


router = DefaultRouter()

app_name = "training"
router.register(r"training", api_views.TrainingViewSet, basename="api-training")

urlpatterns = [
    path("api/", include(router.urls)),
    path(route="schedule", view=training_views.ScheduleView.as_view(), name="schedule"),
    path(
        route="schedule/v1",
        view=training_views.ScheduleV1View.as_view(),
        name="schedule-v1",
    ),
    path(
        route="schedule/<str:date>/",
        view=training_views.TrainingByDateView.as_view(),
        name="training-types",
    ),
    path(
        route="schedule/slot/<int:pk>/",
        view=training_views.TrainingSlotView.as_view(),
        name="select_space",
    ),
    path(
        route="schedule-done/<str:pk>",
        view=training_views.ScheduleDoneView.as_view(),
        name="schedule-done",
    ),
    path(
        route="my-schedule",
        view=training_views.MyScheduleView.as_view(),
        name="my_schedule",
    ),
    path(route="info", view=training_views.InfoView.as_view(), name="info"),
    path(
        route="resumen-2023",
        view=training_views.ResumeYear.as_view(),
        name="resume_year",
    ),
    path(
        route="class-calendar/",
        view=training_views.ClassCalendarView.as_view(),
        name="calendar",
    ),
    path(
        route="class-calendar/<str:day>/",
        view=training_views.ClassCalendarDetailView.as_view(),
        name="detail-calendar",
    ),
]

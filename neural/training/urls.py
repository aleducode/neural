from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import include


from neural.training import views as training_views
from neural.training import api as api_views


router = DefaultRouter()
app_name = "training"

router.register(r'training', api_views.TrainingViewSet, basename='api-training')
urlpatterns = [
    path('api/', include(router.urls)),
    path(
        route='schedule',
        view=training_views.ScheduleView.as_view(),
        name='schedule'
    ),

]

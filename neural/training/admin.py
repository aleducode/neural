"""Training admin."""

from django.contrib import admin
from neural.training.models import UserTraining, Slot, Space, ImagePopUp, TrainingType, Classes
from neural.training.forms import ImagePopUpForm


class UserTrainingInline(admin.TabularInline):
    model = UserTraining
    extra = 0
    autocomplete_fields = ['user']


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_filter = ['date']
    list_display = ['date']
    inlines = [UserTrainingInline]

@admin.register(TrainingType)
class TrainingTypeAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ['name', "slug_name"]
    readonly_fields = ['slug_name']

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_filter = ['day']
    list_display = ['get_day_display', "training_type", "hour_init", "hour_end"]

    def get_day_display(self, obj):
        return obj.get_day_display()


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTraining)
class UserTrainingAdmin(admin.ModelAdmin):
    list_display = ['user', 'slot', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']


@admin.register(ImagePopUp)
class ImagePopUpAdmin(admin.ModelAdmin):
    list_display = ["image_name", "image", "is_active"]
    form = ImagePopUpForm

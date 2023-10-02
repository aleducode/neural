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
    list_display = ['date', "class_training_name", "class_training_hour_init", "class_training_hour_end", "max_places"]
    inlines = [UserTrainingInline]

    def class_training_hour_init(self, obj):
        if obj.class_trainging:
            return obj.class_trainging.hour_init
        return None

    def class_training_hour_end(self, obj):
        if obj.class_trainging:
            return obj.class_trainging.hour_end
        return None

    def class_training_name(self, obj):
        if obj.class_trainging.training_type:
            return obj.class_trainging.training_type.name
        return None


@admin.register(TrainingType)
class TrainingTypeAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ['name', "slug_name"]
    readonly_fields = ['slug_name']


@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_filter = ['day']
    list_display = ['day', "training_type", "hour_init", "hour_end"]


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

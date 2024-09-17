"""Training admin."""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from neural.training.models import (
    UserTraining,
    Slot,
    Space,
    ImagePopUp,
    TrainingType,
    Classes,
)
from neural.training.forms import ImagePopUpForm


class UserTrainingInline(admin.TabularInline):
    model = UserTraining
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    date_hierarchy = "date"
    list_filter = ["date"]
    list_display = [
        "date",
        "class_training_name",
        "class_training_hour_init",
        "class_training_hour_end",
        "max_places",
    ]
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
    list_filter = ["name"]
    list_display = ["name", "slug_name"]
    readonly_fields = ["slug_name"]


@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_filter = ["day"]
    list_display = ["day", "training_type", "hour_init", "hour_end"]

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if obj.slots.get().user_trainings.exists():
            error_message = (
                "No se puede eliminar esta Clase porque tiene entrenamientos agendados."
            )
            self.message_user(request, error_message, level="error")
            return HttpResponseRedirect(
                reverse("admin:training_classes_change", args=[object_id])
            )

        return super().delete_view(request, object_id, extra_context=extra_context)


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTraining)
class UserTrainingAdmin(admin.ModelAdmin):
    list_display = ["user", "slot_info", "status"]
    search_fields = ["user__first_name", "user__last_name", "user__email"]

    def slot_info(self, obj):
        slot = obj.slot
        if slot:
            slot_info_str = f"{slot.date} {slot.class_trainging.hour_init} - {slot.class_trainging.hour_end}"
        else:
            slot_info_str = "N/A"
        return slot_info_str


@admin.register(ImagePopUp)
class ImagePopUpAdmin(admin.ModelAdmin):
    list_display = ["image_name", "image", "is_active"]
    form = ImagePopUpForm

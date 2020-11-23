"""Training admin."""

from django.contrib import admin
from neural.training.models import UserTraining, Slot


class UserTrainingInline(admin.TabularInline):
    model = UserTraining
    extra = 0
    autocomplete_fields = ['user']


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_filter = ['date', 'hour_init']
    list_display = ['__str__', 'date', 'hour_init']
    inlines = [UserTrainingInline]

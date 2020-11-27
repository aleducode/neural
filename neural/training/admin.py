"""Training admin."""

from django.contrib import admin
from neural.training.models import UserTraining, Slot, Space, Temperature


class UserTrainingInline(admin.TabularInline):
    model = UserTraining
    extra = 0
    autocomplete_fields = ['user']


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_filter = ['date', 'hour_init']
    list_display = ['pk', '__str__', 'date', 'hour_init', 'available_places']
    inlines = [UserTrainingInline]


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    pass

@admin.register(Temperature)
class TemperatureAdmin(admin.ModelAdmin):
    list_display = ['user', 'temperature']


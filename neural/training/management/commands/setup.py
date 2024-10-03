"""Sync Command."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.training.models import TrainingType, Classes, Slot
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Handle command usage."""
        names = ["Grupal running", "Grupal formativo", "Grupal preparación física"]
        for name in names:
            training_type, _ = TrainingType.objects.get_or_create(name=name)
            # For today into each day until 3 months
            for i in range(0, 30):
                date = timezone.now() + timedelta(days=i)
                # Only weekdays
                if date.weekday() < 5:
                    hours = {
                        "Grupal running": [
                            {"start": "05:30", "end": "06:30"},
                            {"start": "19:00", "end": "20:00"},
                        ],
                        "Grupal formativo": [
                            {"start": "16:00", "end": "17:00"},
                            {"start": "17:00", "end": "18:00"},
                        ],
                        "Grupal preparación física": [
                            {"start": "15:00", "end": "16:00"},
                            {"start": "18:00", "end": "19:00"},
                        ],
                    }
                    day_choice = Classes.DaysChoices(date.strftime("%A").upper())
                    for hour in hours.get(name):
                        session, _ = Classes.objects.get_or_create(
                            day=day_choice,
                            training_type=training_type,
                            defaults=dict(
                                hour_init=hour.get("start"),
                                hour_end=hour.get("end"),
                            ),
                        )
                        Slot.objects.update_or_create(
                            date=date,
                            class_trainging=session,
                            defaults={"max_places": 8},
                        )

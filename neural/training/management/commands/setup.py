"""Sync Command."""
import calendar
from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.training.models import Slot, Classes
from datetime import timedelta, date


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Handle command usage."""
        wrapper_days = {
            0: 'MONDAY',
            1: 'TUESDAY',
            2: 'WEDNESDAY',
            3: 'THURSDAY',
            4: 'FRIDAY',
            5: 'SATURDAY',
            6: 'SUNDAY'
        }
        now = date(2023, 9, 28)
        result = []
        for i in range(0, 7):
            day = now + timedelta(days=i)
            day_name = wrapper_days.get(day.weekday())
            classes = Classes.objects.filter(day=day_name)
            for session in classes:
                slot, created = Slot.objects.update_or_create(
                    date=day,
                    class_trainging=session,
                    defaults={
                        'max_places': 20
                    }
                )
                result.append(slot.pk)
        Slot.objects.filter(date__gte=timezone.now()).exclude(pk__in=result).delete()

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
        now = date(2023, 10, 1)
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
        class_training = Classes.objects.filter(training_type__slug_name="funcional-training").first()
        old_slots = Slot.objects.filter(date__lt=now)
        for slot in old_slots:
            slot.class_trainging = class_training
            slot.save()
        Slot.objects.filter(date__gte=timezone.now()).exclude(pk__in=result).delete()

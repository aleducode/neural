"""Sync Command."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.training.models import Slot
from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Handle command usage."""
        Slot.objects.all().delete()
        sessions = {
            1: {
                'NEURAL_CIRCUIT': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '6:20',
                        'end': '7:20'
                    },
                    {
                        'init': '7:40',
                        'end': '8:40'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '17:20',
                        'end': '18:20'
                    },
                    {
                        'init': '18:40',
                        'end': '18:40'
                    },
                ],
                'BALANCE': [
                    {
                        'init': '19:00',
                        'end': '20:00'
                    },
                ],
            },
            2: {
                'NEURAL_CIRCUIT': [],
                'POWER_HOUR': []
            },
            3: {
                'WORKOUT': [],
                'NEURAL_CIRCUIT': []
            }
        }

        now = timezone.localdate()
        days = 7
        Slot.objects.all().delete()
        for i in range(0, days):
            day = now + timedelta(days=i)
            for session in sessions:
                Slot.objects.get_or_create(
                    date=day,
                    hour_init=session.get('init'),
                    hour_end=session.get('end'),
                    max_places=10
                )

"""Sync Command."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.training.models import Slot


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Handle command usage."""
        sessions = {
            'FUNCTIONAL': [
                {
                    'init': '9:00',
                    'end': '10:00'
                },
                {
                    'init': '11:00',
                    'end': '12:00'
                },
                  {
                    'init': '13:00',
                    'end': '14:00'
                }
            ]
        }
        now = timezone.localdate()
        for session in sessions.get('FUNCTIONAL'):
            Slot.objects.get_or_create(
                date=now,
                hour_init=session.get('init'),
                hour_end=session.get('end'),
                max_places=12
            )

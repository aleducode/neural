"""Sync Command."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.training.models import Slot
from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Handle command usage."""
        sessions = {
            1: {
                'FUNCIONAL_TRAINING': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                    {
                        'init': '8:00',
                        'end': '9:00'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '17:00',
                        'end': '18:00'
                    },
                    {
                        'init': '18:00',
                        'end': '19:00'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    },

                ],
                'GAP_MMSS': [
                    {
                        'init': '6:00',
                        'end': '7:00'
                    },
                ],
                'CARDIO_STEP': [
                    {
                        'init': '19:00',
                        'end': '20:00'
                    },
                ]
            },
            2: {
                'RTG': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '17:00',
                        'end': '18:00'
                    },
                ],
                'FUNCIONAL_TRAINING': [
                    {
                        'init': '6:00',
                        'end': '7:00'
                    },
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                    {
                        'init': '8:00',
                        'end': '9:00'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '18:00',
                        'end': '19:00'
                    },
                    {
                        'init': '19:00',
                        'end': '20:00'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    },

                ],
            },
            3: {
                'FUNCIONAL_TRAINING': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '6:00',
                        'end': '7:00'
                    },
                    {
                        'init': '8:00',
                        'end': '9:00'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '17:00',
                        'end': '18:00'
                    },
                    {
                        'init': '19:00',
                        'end': '20:00'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    },
                ],
                'BALANCE': [
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                ],
                'GAP_MMSS': [
                    {
                        'init': '18:00',
                        'end': '19:00'
                    },
                ],
            },
            4: {

                'FUNCIONAL_TRAINING': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '6:00',
                        'end': '7:00'
                    },
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '17:00',
                        'end': '18:00'
                    },
                    {
                        'init': '18:00',
                        'end': '19:00'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    },

                ],
                'SUPERSTAR': [
                    {
                        'init': '08:00',
                        'end': '09:00'
                    },
                ],
                'FIT_BOXING': [
                    {
                        'init': '19:00',
                        'end': '20:00'
                    },
                ],
            },
            5: {
                'FUNCIONAL_TRAINING': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                    {
                        'init': '6:00',
                        'end': '7:00'
                    },
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                    {
                        'init': '8:00',
                        'end': '9:00'
                    },
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                    {
                        'init': '16:00',
                        'end': '17:00'
                    },
                    {
                        'init': '17:00',
                        'end': '18:00'
                    },
                    {
                        'init': '18:00',
                        'end': '19:00'
                    },
                    {
                        'init': '19:00',
                        'end': '20:00'
                    }
                ],
            },
            6: {
                'PILATES': [
                    {
                        'init': '8:00',
                        'end': '9:00'
                    },
                ],
                'SUPERSTAR': [
                    {
                        'init': '9:00',
                        'end': '10:00'
                    },
                ],
                'FUNCIONAL_TRAINING': [
                    {
                        'init': '10:00',
                        'end': '11:00'
                    },
                ],
                'CARDIOHIT': [
                    {
                        'init': '11:00',
                        'end': '12:00'
                    },
                ],
            },
            7: {
            },
        }

        now = timezone.localdate()
        days = 74
        result = []
        for i in range(0, days):
            day = now + timedelta(days=i)
            for session in sessions:
                now_data = sessions[day.isoweekday()]
                for training in now_data:
                    for hour in now_data[training]:
                        slot, created = Slot.objects.update_or_create(
                            date=day,
                            hour_init=hour.get('init'),
                            training_type=training,
                            defaults={
                                'hour_end': hour.get('end'),
                                'max_places': 12
                            }
                        )
                        result.append(slot.pk)
        Slot.objects.filter(date__gte=timezone.now()).exclude(pk__in=result).delete()

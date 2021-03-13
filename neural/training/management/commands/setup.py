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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '18:10',
                        'end': '19:10'
                    },
                    {
                        'init': '20:30',
                        'end': '21:30'
                    },

                ],
                'WORKOUT': [
                    {
                        'init': '19:20',
                        'end': '20:20'
                    },
                ]
            },
            2: {
                'POWER_HOUR': [
                    {
                        'init': '5:00',
                        'end': '6:00'
                    },
                ],
                'NEURAL_CIRCUIT': [
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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '18:10',
                        'end': '19:10'
                    },
                    {
                        'init': '19:20',
                        'end': '20:20'
                    },
                    {
                        'init': '20:30',
                        'end': '21:30'
                    },

                ]
            },
            3: {
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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '18:10',
                        'end': '19:10'
                    },
                    {
                        'init': '19:20',
                        'end': '20:20'
                    },
                    {
                        'init': '20:30',
                        'end': '21:30'
                    },
                ]},
            4: {
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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '18:10',
                        'end': '19:10'
                    },
                    {
                        'init': '19:20',
                        'end': '20:20'
                    },

                ],
                'SPECIAL': [
                    {
                        'init': '20:30',
                        'end': '21:30'
                    },
                ],

            },
            5: {
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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '18:10',
                        'end': '19:10'
                    },
                    {
                        'init': '19:20',
                        'end': '20:20'
                    },
                ]
            },
            6: {
                'BALANCE': [
                    {
                        'init': '7:00',
                        'end': '8:00'
                    },
                ],
                'NEURAL_CIRCUIT': [
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
                        'init': '11:00',
                        'end': '12:00'
                    },
                ],
            }
        }

        now = timezone.localdate()
        days = 30
        result = []
        for i in range(0, days):
            day = now + timedelta(days=i)
            for session in sessions:
                if day.isoweekday() != 7:
                    now_data = sessions[day.isoweekday()]
                    for training in now_data:
                        for hour in now_data[training]:
                            slot, created = Slot.objects.update_or_create(
                                date=day,
                                hour_init=hour.get('init'),
                                defaults={
                                    'training_type': training,
                                    'hour_end': hour.get('end'),
                                    'max_places': 12
                                }
                            )
                            result.append(slot.pk)
        Slot.objects.filter(date__gte=timezone.now()).exclude(pk__in=result).delete()

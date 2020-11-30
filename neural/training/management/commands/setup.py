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
                        'init': '10:20',
                        'end': '11:20'
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
                        'init': '20:00',
                        'end': '21:00'
                    }
                ],
                'WORKOUT': [
                    {
                        'init': '18:40',
                        'end': '19:40'
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
                        'init': '17:20',
                        'end': '18:20'
                    },
                    {
                        'init': '18:40',
                        'end': '19:40'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    },
                ],
            },
            3: {
                'WORKOUT': [
                    {
                        'init': '6:20',
                        'end': '7:20'
                    },
                ],
                'NEURAL_CIRCUIT': [
                    {
                        'init': '5:00',
                        'end': '6:00'
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
                        'init': '17:20',
                        'end': '18:20'
                    },
                    {
                        'init': '18:40',
                        'end': '19:40'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
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
                        'init': '17:20',
                        'end': '18:20'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    }

                ]

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
                        'init': '17:20',
                        'end': '18:20'
                    },
                    {
                        'init': '18:40',
                        'end': '19:40'
                    },
                    {
                        'init': '20:00',
                        'end': '21:00'
                    }
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
                        'init': '8:20',
                        'end': '9:20'
                    },
                    {
                        'init': '9:40',
                        'end': '10:40'
                    },
                ],
                'POWER_HOUR': [
                    {
                        'init': '11:00',
                        'end': '12:00'
                    },
                ],
            }
        }

        now = timezone.localdate()
        days = 6
        for i in range(0, days):
            day = now + timedelta(days=i)
            for session in sessions:
                if day.isoweekday() != 7:
                    now_data = sessions[day.isoweekday()]
                    for training in now_data:
                        for hour in now_data[training]:
                            Slot.objects.get_or_create(
                                training_type=training,
                                date=day,
                                hour_init=hour.get('init'),
                                defaults={
                                    'hour_end': hour.get('end'),
                                    'max_places': 10
                                }
                            )

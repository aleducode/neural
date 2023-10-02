"""Sync Command."""

# Django
from django.core.management.base import BaseCommand

# Models
from neural.training.models import TrainingType, Classes


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Handle command usage."""

        sessions = [
            {
                "day": "MONDAY",
                "training_type": {
                    'funcional-training': [
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
                        },
                        {
                            'init': '20:00',
                            'end': '21:00'
                        },
                    ],
                    'funcional-box': [
                        {
                            'init': '7:00',
                            'end': '8:00'
                        },
                    ]
                }
            },
            {
                "day": "TUESDAY",
                "training_type": {
                    'funcional-training': [
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
                        },
                        {
                            'init': '20:00',
                            'end': '21:00'
                        },
                    ]
                }
            },
            {
                "day": "WEDNESDAY",
                "training_type": {
                    'funcional-training': [
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
                            'init': '19:00',
                            'end': '20:00'
                        },
                        {
                            'init': '20:00',
                            'end': '21:00'
                        },
                    ],
                    'gap': [
                        {
                            'init': '6:00',
                            'end': '7:00'
                        },
                        {
                            'init': '18:00',
                            'end': '19:00'
                        },
                    ]
                }
            },
            {
                "day": "THURSDAY",
                "training_type": {
                    'funcional-training': [
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
                            'init': '20:00',
                            'end': '21:00'
                        },
                    ],
                    'balance': [
                        {
                            'init': '19:00',
                            'end': '20:00'
                        },
                    ]
                }
            },
            {
                "day": "FRIDAY",
                "training_type": {
                    'funcional-training': [
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
                        },
                    ],
                }
            },
            {
                "day": "SARTURDAY",
                "training_type": {
                    'funcional-training': [
                        {
                            'init': '10:00',
                            'end': '11:00'
                        },
                    ],
                    'a-fuego': [
                        {
                            'init': '7:30',
                            'end': '8:30'
                        },
                    ],
                    'super-star': [
                        {
                            'init': '9:00',
                            'end': '10:00'
                        },
                    ],
                    'rumba': [
                        {
                            'init': '11:00',
                            'end': '12:00'
                        },
                    ],
                },
            },
            {
                "day": "SUNDAY",
                "training_type": {
                    'funcional-training': [
                        {
                            'init': '09:00',
                            'end': '10:00'
                        },
                    ],
                    'aeroibic-step': [
                        {
                            'init': '10:00',
                            'end': '11:00'
                        },
                    ],
                }
            },
        ]
        for session in sessions:
            day = session.get("day")
            training_data = session.get("training_type")
            for training_type, training_hours in training_data.items():
                training_instance = TrainingType.objects.get(slug_name=training_type)
                for hour in training_hours:
                    init = hour.get('init')
                    end = hour.get('end')
                    Classes.objects.create(day=day, training_type=training_instance, hour_init=init, hour_end=end)
        print("Finish")

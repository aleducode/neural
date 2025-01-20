"""Sync Command."""

from django.core.management.base import BaseCommand
from neural.users.models import NeuralPlan, UserMembership


plans_dict = [
    {
        "name": "Mensualidad",
        "description": "Mensualidad de entrenamiento",
        "price": 150000,
        "duration": 30,
    },
    {
        "name": "Trimestre",
        "description": "Trimestre de entrenamiento",
        "price": 450000,
        "duration": 90,
    },
    {
        "name": "Semestre",
        "description": "Semestre de entrenamiento",
        "price": 900000,
        "duration": 180,
    },
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Handle command usage."""
        for i in plans_dict:
            NeuralPlan.objects.get_or_create(
                name=i.get("name"),
                description=i.get("description"),
                price=i.get("price"),
                duration=i.get("duration"),
            )
            print(f"Plan {i.get('name')} created")
        dict_plans = {
            "MENSUAL": "Mensualidad",
            "QUARTER": "Trimestre",
            "SEMESTER": "Semestre",
        }
        for e in UserMembership.objects.filter(plan__isnull=True):
            plan = NeuralPlan.objects.filter(name=dict_plans.get(e.membership_type))
            if plan:
                e.plan = plan.first()
                e.save()
                print(f"Plan {plan.first()} assigned to user {e.user}")

"""Sync Command."""

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from neural.users.models import User, Ranking
from neural.training.models import UserTraining


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Handle command usage."""
        Ranking.objects.all().delete()
        all_user_training = (
            UserTraining.objects.filter(
                slot__date__year=timezone.now().year,
                status=UserTraining.Status.CONFIRMED,
            )
            .values("user")
            .annotate(
                training_count=Count("user"),
            )
            .order_by("-training_count")
            .exclude(user__pk=13)
            .distinct()
        )
        index = 1
        for user_data in all_user_training:
            user = User.objects.get(pk=user_data["user"])
            user.rankings.update_or_create(
                position=index,
                trainings=user_data.get("training_count", 0),
            )
            print(
                f"User {user} updated with {index} position and {user_data.get('training_count', 0)} trainings"
            )
            index += 1

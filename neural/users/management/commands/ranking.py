"""Ranking Command - Generate yearly rankings for Year in Review."""

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from neural.users.models import User, Ranking
from neural.training.models import UserTraining


class Command(BaseCommand):
    help = "Generate user rankings for Year in Review"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=timezone.localdate().year,
            help="Year to generate rankings for (default: current year)",
        )

    def handle(self, *args, **options):
        """Handle command usage."""
        year = options["year"]
        self.stdout.write(f"Generating rankings for {year}...")

        # Clear existing rankings
        Ranking.objects.all().delete()

        # Get all user trainings for the year
        all_user_training = (
            UserTraining.objects.filter(
                slot__date__year=year,
                status__in=[UserTraining.Status.CONFIRMED, UserTraining.Status.DONE],
            )
            .values("user")
            .annotate(
                training_count=Count("user"),
            )
            .order_by("-training_count")
            .distinct()
        )

        index = 1
        for user_data in all_user_training:
            user = User.objects.get(pk=user_data["user"])
            user.rankings.update_or_create(
                position=index,
                defaults={"trainings": user_data.get("training_count", 0)},
            )
            self.stdout.write(
                f"#{index} - {user.email}: {user_data.get('training_count', 0)} trainings"
            )
            index += 1

        self.stdout.write(
            self.style.SUCCESS(f"Rankings generated for {index - 1} users")
        )

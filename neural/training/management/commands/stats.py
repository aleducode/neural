"""Sync Command."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from neural.users.models import User, UserStrike
from datetime import timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Handle command usage."""
        year = timezone.now().year
        current_week = timezone.now().isocalendar()[1]

        for user in User.objects.all():
            user.email = user.email.lower()
            user.save()
            current_streak_weeks = 0
            current_strike = None

            # Iterate over all weeks in the year
            for week in range(1, current_week + 1):
                # Calculate the date range using your method
                init_date = timezone.now().date().replace(year=year, month=1, day=1)
                end_date = init_date + timedelta(days=7)

                # Get trainings for this week
                trainings_in_week = user.trainings.filter(
                    slot__date__range=[init_date, end_date]
                )

                # Update or create stats for this week
                user.stats.update_or_create(
                    year=year,
                    week=week,
                    defaults={
                        "trainings": trainings_in_week.count(),
                        "calories": trainings_in_week.count() * 400,
                        "hours": trainings_in_week.count() * 1,
                    },
                )

                # Strike logic
                if trainings_in_week.exists():
                    current_streak_weeks += 1

                    if current_strike is None:
                        # Create new strike instance
                        current_strike = UserStrike.objects.create(
                            user=user,
                            weeks=current_streak_weeks,
                            is_current=True,
                            last_week=week,
                        )
                    else:
                        # Update existing strike
                        current_strike.weeks = current_streak_weeks
                        current_strike.last_week = week
                        current_strike.save()
                else:
                    # No training this week - break the streak
                    if current_strike:
                        current_strike.is_current = False
                        current_strike.save()
                        current_strike = None
                    current_streak_weeks = 0

            self.stdout.write(
                self.style.SUCCESS(
                    f"User {user}: Final streak: {current_streak_weeks} weeks, "
                    + f'Last week: {current_strike.last_week if current_strike else "N/A"}'
                )
            )

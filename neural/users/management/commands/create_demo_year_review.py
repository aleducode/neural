"""
Management command to create demo data for Year in Review feature.
Run with: python manage.py create_demo_year_review
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from neural.users.models import (
    User,
    UserStats,
    UserStrike,
    Ranking,
    UserMembership,
    NeuralPlan,
)
from neural.training.models import TrainingType, Classes, Slot, UserTraining, Space


class Command(BaseCommand):
    help = "Create demo data for Year in Review feature"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="demo@neural.com",
            help="Email for demo user",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=timezone.localdate().year,
            help="Year to generate data for",
        )

    def handle(self, *args, **options):
        email = options["email"]
        year = options["year"]

        self.stdout.write(f"Creating demo data for year {year}...")

        # 1. Create or get demo user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": "demo_user",
                "first_name": "Carlos",
                "last_name": "Demo",
                "phone_number": "3001234567",
                "is_verified": True,
                "is_client": True,
            },
        )
        if created:
            user.set_password("demo123456")
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {email}"))
        else:
            self.stdout.write(f"Using existing user: {email}")

        # 2. Create training types if not exist
        training_types_data = [
            {"name": "Funcional", "slug_name": "funcional", "is_group": True},
            {"name": "CrossFit", "slug_name": "crossfit", "is_group": True},
            {"name": "Yoga", "slug_name": "yoga", "is_group": True},
            {"name": "HIIT", "slug_name": "hiit", "is_group": True},
        ]
        training_types = []
        for tt_data in training_types_data:
            tt, _ = TrainingType.objects.get_or_create(
                slug_name=tt_data["slug_name"],
                defaults=tt_data,
            )
            training_types.append(tt)
        self.stdout.write(f"Training types: {len(training_types)}")

        # 3. Create space if not exist
        space, _ = Space.objects.get_or_create(
            slug_name="sala_principal",
            defaults={"name": "Sala Principal", "description": "Sala de entrenamiento"},
        )

        # 4. Create classes for each training type
        hours = [
            ("06:00", "07:00"),
            ("07:00", "08:00"),
            ("08:00", "09:00"),
            ("17:00", "18:00"),
            ("18:00", "19:00"),
            ("19:00", "20:00"),
        ]
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]

        classes_created = 0
        for tt in training_types:
            for day in days:
                hour_init, hour_end = random.choice(hours)
                cls, created = Classes.objects.get_or_create(
                    training_type=tt,
                    day=day,
                    hour_init=hour_init,
                    hour_end=hour_end,
                )
                if created:
                    classes_created += 1
        self.stdout.write(f"Classes created/verified: {classes_created}")

        # 5. Generate weekly stats for the year (simulate ~3-5 trainings per week)
        UserStats.objects.filter(user=user, year=year).delete()

        total_trainings = 0
        total_calories = 0
        total_hours = 0

        # Simulate activity with some variation (more active in some months)
        month_multipliers = {
            1: 0.8,  # Enero - New year resolution
            2: 0.9,
            3: 1.0,
            4: 1.1,
            5: 1.2,  # Getting stronger
            6: 1.0,
            7: 0.7,  # Vacation
            8: 0.8,
            9: 1.1,  # Back to routine
            10: 1.2,
            11: 1.3,  # Peak
            12: 0.9,  # Holidays
        }

        for week in range(1, 53):
            # Determine month for this week
            week_date = date(year, 1, 1) + timedelta(weeks=week - 1)
            if week_date.year != year:
                continue

            month = week_date.month
            multiplier = month_multipliers.get(month, 1.0)

            # Random trainings with monthly variation
            base_trainings = random.randint(2, 5)
            trainings = max(1, int(base_trainings * multiplier))
            calories = trainings * 400
            hours = trainings

            UserStats.objects.create(
                user=user,
                year=year,
                week=week,
                trainings=trainings,
                calories=calories,
                hours=hours,
            )

            total_trainings += trainings
            total_calories += calories
            total_hours += hours

        self.stdout.write(
            f"Stats created: {total_trainings} trainings, "
            f"{total_calories} calories, {total_hours} hours"
        )

        # 6. Create UserTraining records for detailed analysis
        UserTraining.objects.filter(user=user, slot__date__year=year).delete()

        all_classes = list(Classes.objects.all())
        if not all_classes:
            self.stdout.write(
                self.style.WARNING("No classes found, skipping UserTraining")
            )
        else:
            trainings_created = 0
            start_date = date(year, 1, 1)
            end_date = min(date(year, 12, 31), timezone.localdate())

            current_date = start_date
            while current_date <= end_date:
                # Skip some days randomly
                if random.random() < 0.6:  # 60% chance to train on any given day
                    cls = random.choice(all_classes)

                    # Create or get slot
                    slot, _ = Slot.objects.get_or_create(
                        date=current_date,
                        class_training=cls,
                        defaults={"max_places": 15},
                    )

                    # Create training record
                    UserTraining.objects.create(
                        user=user,
                        slot=slot,
                        status=UserTraining.Status.DONE,
                        space=space,
                    )
                    trainings_created += 1

                current_date += timedelta(days=1)

            self.stdout.write(f"UserTraining records created: {trainings_created}")

        # 7. Create strikes
        UserStrike.objects.filter(user=user).delete()

        # Best streak (historical)
        UserStrike.objects.create(
            user=user,
            weeks=random.randint(8, 16),
            is_current=False,
            last_week=30,
        )

        # Current streak
        current_week = timezone.localdate().isocalendar()[1]
        UserStrike.objects.create(
            user=user,
            weeks=random.randint(3, 8),
            is_current=True,
            last_week=current_week,
        )
        self.stdout.write("Strikes created")

        # 8. Create ranking
        Ranking.objects.filter(user=user).delete()

        # Get a position that makes sense
        total_users = User.objects.filter(is_verified=True, is_client=True).count()
        position = random.randint(1, max(1, min(10, total_users)))

        # Make sure position is unique
        while Ranking.objects.filter(position=position).exists():
            position += 1

        Ranking.objects.create(
            user=user,
            position=position,
            trainings=total_trainings,
        )
        self.stdout.write(f"Ranking created: position #{position}")

        # 9. Create membership
        UserMembership.objects.filter(user=user, is_active=True).delete()

        plan, _ = NeuralPlan.objects.get_or_create(
            slug_name="mensualidad",
            defaults={
                "name": "Mensualidad",
                "description": "Plan mensual",
                "price": 150000,
                "duration": 30,
            },
        )

        UserMembership.objects.create(
            user=user,
            membership_type="MENSUAL",
            plan=plan,
            is_active=True,
            init_date=timezone.localdate() - timedelta(days=15),
            expiration_date=timezone.localdate() + timedelta(days=15),
        )
        self.stdout.write("Membership created")

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("Demo data created successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(f"Email: {email}")
        self.stdout.write("Password: demo123456")
        self.stdout.write(f"Year: {year}")
        self.stdout.write(f"Total trainings: {total_trainings}")
        self.stdout.write("URL: /year-in-review/")
        self.stdout.write(self.style.SUCCESS("=" * 50))

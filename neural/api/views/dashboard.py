"""Dashboard views for API v1."""

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.training.models import UserTraining
from neural.users.models import UserMembership, UserStats, UserStrike


class DashboardView(APIView):
    """Dashboard data view."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.localtime()
        today = now.date()

        # User basic info
        user_data = {
            "first_name": user.first_name,
            "photo": (
                request.build_absolute_uri(user.photo.url) if user.photo else None
            ),
        }

        # Next training
        next_training = None
        upcoming = (
            UserTraining.objects.filter(
                user=user,
                status=UserTraining.Status.CONFIRMED,
                slot__date__gte=today,
            )
            .select_related(
                "slot", "slot__class_training", "slot__class_training__training_type"
            )
            .order_by("slot__date", "slot__class_training__hour_init")
            .first()
        )

        if upcoming:
            slot = upcoming.slot
            training_type = slot.class_training.training_type.name

            # Determine day name
            if slot.date == today:
                day_name = "Hoy"
            elif slot.date == today + timezone.timedelta(days=1):
                day_name = "Mañana"
            else:
                day_names = {
                    0: "Lunes",
                    1: "Martes",
                    2: "Miércoles",
                    3: "Jueves",
                    4: "Viernes",
                    5: "Sábado",
                    6: "Domingo",
                }
                day_name = day_names.get(slot.date.weekday(), "")

            hour = slot.class_training.hour_init.strftime("%I:%M %p")

            next_training = {
                "id": upcoming.id,
                "day_name": day_name,
                "hour": hour,
                "training_type": training_type,
                "message": f"Recuerda: Tu próximo entrenamiento es {training_type} {day_name} a las {hour}",
            }

        # Current strike
        strike_data = {"weeks": 0, "is_current": False}
        current_strike = UserStrike.objects.filter(user=user, is_current=True).first()
        if current_strike:
            strike_data = {
                "weeks": current_strike.weeks,
                "is_current": True,
            }

        # Weekly stats
        current_week = now.isocalendar()[1]
        stats_data = {"trainings": 0, "calories": 0, "hours": 0}
        weekly_stats = UserStats.objects.filter(
            user=user, week=current_week, year=now.year
        ).first()
        if weekly_stats:
            stats_data = {
                "trainings": weekly_stats.trainings,
                "calories": weekly_stats.calories,
                "hours": weekly_stats.hours,
            }

        # Active membership
        membership_data = None
        active_membership = (
            UserMembership.objects.filter(user=user, is_active=True)
            .select_related("plan")
            .first()
        )
        if active_membership:
            membership_data = {
                "plan_name": active_membership.plan.name
                if active_membership.plan
                else active_membership.membership_type,
                "days_left": active_membership.days_left,
                "is_active": True,
                "expiration_date": active_membership.expiration_date.isoformat()
                if active_membership.expiration_date
                else None,
            }

        # Has year review
        year = now.year
        has_year_review = UserTraining.objects.filter(
            user=user,
            status=UserTraining.Status.CONFIRMED,
            slot__date__year=year,
        ).exists()

        return Response(
            {
                "user": user_data,
                "next_training": next_training,
                "strike": strike_data,
                "stats": stats_data,
                "membership": membership_data,
                "has_year_review": has_year_review,
            }
        )

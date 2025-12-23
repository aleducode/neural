"""Year in Review views for API v1."""

from collections import Counter

from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractWeekDay
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.training.models import UserTraining
from neural.users.models import Ranking, UserStats, UserStrike


class YearReviewView(APIView):
    """Get year in review statistics."""

    permission_classes = [IsAuthenticated]

    def get(self, request, year=None):
        user = request.user

        if year is None:
            year = timezone.localtime().year

        # Validate year
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = timezone.localtime().year

        # Get all trainings for the year
        trainings = UserTraining.objects.filter(
            user=user,
            status=UserTraining.Status.CONFIRMED,
            slot__date__year=year,
        ).select_related("slot", "slot__class_training", "slot__class_training__training_type")

        total_trainings = trainings.count()

        if total_trainings == 0:
            return Response({
                "year": year,
                "total_trainings": 0,
                "message": "No tienes entrenamientos registrados para este año",
            })

        # Basic stats
        total_calories = total_trainings * 400
        total_hours = total_trainings

        # Active weeks
        weekly_stats = UserStats.objects.filter(
            user=user, year=year, trainings__gt=0
        )
        active_weeks = weekly_stats.count()
        avg_trainings_per_week = (
            total_trainings / active_weeks if active_weeks > 0 else 0
        )

        # Monthly distribution
        monthly_data = [0] * 12
        monthly_counts = (
            trainings.annotate(month=ExtractMonth("slot__date"))
            .values("month")
            .annotate(count=Count("id"))
        )
        for item in monthly_counts:
            monthly_data[item["month"] - 1] = item["count"]

        # Best month
        best_month_idx = monthly_data.index(max(monthly_data))
        month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        best_month = {
            "name": month_names[best_month_idx],
            "trainings": monthly_data[best_month_idx],
        }

        # Favorite training type
        training_types = []
        for t in trainings:
            if t.slot and t.slot.class_training:
                training_types.append(t.slot.class_training.training_type.name)

        if training_types:
            type_counter = Counter(training_types)
            favorite_type, favorite_count = type_counter.most_common(1)[0]
            favorite_training = {"type": favorite_type, "count": favorite_count}
        else:
            favorite_training = {"type": "N/A", "count": 0}

        # Favorite day of week
        weekday_data = [0] * 7
        day_counts = (
            trainings.annotate(weekday=ExtractWeekDay("slot__date"))
            .values("weekday")
            .annotate(count=Count("id"))
        )
        for item in day_counts:
            # Django weekday: 1=Sunday, 2=Monday, ..., 7=Saturday
            # Convert to 0=Monday, ..., 6=Sunday
            idx = (item["weekday"] - 2) % 7
            weekday_data[idx] = item["count"]

        day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        favorite_day_idx = weekday_data.index(max(weekday_data))
        favorite_day = {
            "name": day_names[favorite_day_idx],
            "count": weekday_data[favorite_day_idx],
        }

        # Favorite time of day
        morning_count = 0  # 5am - 12pm
        afternoon_count = 0  # 12pm - 6pm
        evening_count = 0  # 6pm - 10pm

        for t in trainings:
            if t.slot and t.slot.class_training:
                hour = t.slot.class_training.hour_init.hour
                if 5 <= hour < 12:
                    morning_count += 1
                elif 12 <= hour < 18:
                    afternoon_count += 1
                else:
                    evening_count += 1

        time_periods = [
            ("Mañana", morning_count, "sunrise"),
            ("Tarde", afternoon_count, "sun"),
            ("Noche", evening_count, "moon"),
        ]
        favorite_time_data = max(time_periods, key=lambda x: x[1])
        favorite_time = {
            "period": favorite_time_data[0],
            "emoji": favorite_time_data[2],
        }

        # Streaks
        best_strike = (
            UserStrike.objects.filter(user=user)
            .order_by("-weeks")
            .first()
        )
        current_strike = UserStrike.objects.filter(
            user=user, is_current=True
        ).first()

        streaks = {
            "best": best_strike.weeks if best_strike else 0,
            "current": current_strike.weeks if current_strike else 0,
        }

        # Ranking
        ranking_data = {"position": None, "total_users": 0}
        user_ranking = Ranking.objects.filter(user=user).first()
        if user_ranking:
            total_ranked = Ranking.objects.count()
            ranking_data = {
                "position": user_ranking.position,
                "total_users": total_ranked,
            }

        # Fun metrics
        pizzas_burned = round(total_calories / 2000, 1)  # ~2000 cal per pizza
        marathons_equivalent = round(total_hours * 6 / 42.195, 1)  # Avg 6km/h, marathon is 42.195km

        return Response({
            "year": year,
            "total_trainings": total_trainings,
            "total_calories": total_calories,
            "total_hours": total_hours,
            "active_weeks": active_weeks,
            "avg_trainings_per_week": round(avg_trainings_per_week, 1),
            "best_month": best_month,
            "favorite_training": favorite_training,
            "favorite_day": favorite_day,
            "favorite_time": favorite_time,
            "streaks": streaks,
            "ranking": ranking_data,
            "fun_metrics": {
                "pizzas_burned": pizzas_burned,
                "marathons_equivalent": marathons_equivalent,
            },
            "monthly_data": monthly_data,
            "weekday_data": weekday_data,
        })

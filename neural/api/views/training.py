"""Training views for API v1."""

from datetime import timedelta

from django.db.models import F
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.api.serializers.training import (
    SlotSerializer,
    UserTrainingSerializer,
)
from neural.training.models import Slot, TrainingType, UserTraining
from neural.users.models import UserStats, UserStrike


class CalendarView(APIView):
    """Get calendar days for the next 7 days."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        days = []

        day_names = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }

        for i in range(7):
            date = today + timedelta(days=i)
            has_slots = Slot.objects.filter(date=date).exists()

            if i == 0:
                day_name = "Hoy"
            elif i == 1:
                day_name = "Mañana"
            else:
                day_name = day_names.get(date.weekday(), "")

            days.append(
                {
                    "date": date.isoformat(),
                    "day_name": day_name,
                    "has_slots": has_slots,
                }
            )

        return Response({"days": days})


class SlotsView(APIView):
    """Get available slots for a specific date."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get("date")
        training_type_slug = request.query_params.get("type")

        if not date_str:
            return Response(
                {"error": "El parámetro 'date' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from datetime import datetime

            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already has a booking for this date
        already_scheduled = UserTraining.objects.filter(
            user=request.user,
            slot__date=date,
            status=UserTraining.Status.CONFIRMED,
        ).exists()

        # Get slots for the date
        slots = Slot.objects.filter(date=date).select_related(
            "class_training", "class_training__training_type"
        )

        # Filter by training type if provided
        if training_type_slug:
            slots = slots.filter(
                class_training__training_type__slug_name=training_type_slug
            )

        # If today, filter by current time + 20 minutes
        now = timezone.localtime()
        if date == now.date():
            cutoff_time = (now + timedelta(minutes=20)).time()
            slots = slots.filter(class_training__hour_init__gte=cutoff_time)

        # Order by hour
        slots = slots.order_by("class_training__hour_init")

        # Day name
        day_names = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }

        return Response(
            {
                "date": date_str,
                "day_name": day_names.get(date.weekday(), ""),
                "already_scheduled": already_scheduled,
                "slots": SlotSerializer(slots, many=True).data,
            }
        )


class SlotDetailView(APIView):
    """Get details of a specific slot."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            slot = Slot.objects.select_related(
                "class_training", "class_training__training_type"
            ).get(id=pk)
        except Slot.DoesNotExist:
            return Response(
                {"error": "Slot no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get confirmed users for this slot
        confirmed_trainings = (
            UserTraining.objects.filter(
                slot=slot,
                status=UserTraining.Status.CONFIRMED,
            )
            .select_related("user")
            .order_by("id")
        )

        confirmed_users = [
            {
                "id": t.user.id,
                "name": f"{t.user.first_name} {t.user.last_name}",
            }
            for t in confirmed_trainings
        ]

        # Check if current user already booked this slot
        user_has_booked = confirmed_trainings.filter(user=request.user).exists()

        # Check if user has any booking for this date
        already_scheduled = UserTraining.objects.filter(
            user=request.user,
            slot__date=slot.date,
            status=UserTraining.Status.CONFIRMED,
        ).exists()

        return Response(
            {
                "slot": SlotSerializer(slot).data,
                "confirmed_users": confirmed_users,
                "confirmed_count": len(confirmed_users),
                "user_has_booked": user_has_booked,
                "already_scheduled_today": already_scheduled,
            }
        )


class BookView(APIView):
    """Book a training slot."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        slot_id = request.data.get("slot_id")

        if not slot_id:
            return Response(
                {"error": "slot_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            slot = Slot.objects.select_related(
                "class_training", "class_training__training_type"
            ).get(id=slot_id)
        except Slot.DoesNotExist:
            return Response(
                {"error": "Slot no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user

        # Check if user is verified
        if not user.is_verified:
            return Response(
                {"error": "Tu cuenta aún no ha sido verificada"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check if user already has a booking for this date
        if UserTraining.objects.filter(
            user=user,
            slot__date=slot.date,
            status=UserTraining.Status.CONFIRMED,
        ).exists():
            return Response(
                {"error": "Ya tienes una reserva para este día"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check availability
        if slot.available_places <= 0:
            return Response(
                {"error": "Este horario ya no tiene cupo disponible"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create booking
        booking = UserTraining.objects.create(
            user=user,
            slot=slot,
            status=UserTraining.Status.CONFIRMED,
        )

        # Update stats
        now = timezone.localtime()
        current_week = now.isocalendar()[1]

        stats, created = UserStats.objects.get_or_create(
            user=user,
            week=current_week,
            year=now.year,
            defaults={"trainings": 0, "calories": 0, "hours": 0},
        )
        stats.trainings = F("trainings") + 1
        stats.calories = F("calories") + 400
        stats.hours = F("hours") + 1
        stats.save()

        # Update strike
        strike, created = UserStrike.objects.get_or_create(
            user=user,
            is_current=True,
            defaults={"weeks": 0, "last_week": 0},
        )

        if strike.last_week != current_week:
            # Check if consecutive week
            if strike.last_week == current_week - 1 or strike.last_week == 0:
                strike.weeks = F("weeks") + 1
            else:
                # Reset strike
                strike.weeks = 1

            strike.last_week = current_week
            strike.save()

        return Response(
            {
                "success": True,
                "booking": UserTrainingSerializer(booking).data,
                "message": "Reserva confirmada exitosamente",
            },
            status=status.HTTP_201_CREATED,
        )


class MyTrainingsView(APIView):
    """Get user's upcoming trainings."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()

        trainings = (
            UserTraining.objects.filter(
                user=request.user,
                status=UserTraining.Status.CONFIRMED,
                slot__date__gte=today,
            )
            .select_related(
                "slot", "slot__class_training", "slot__class_training__training_type"
            )
            .order_by("slot__date", "slot__class_training__hour_init")[:7]
        )

        return Response(
            {
                "trainings": UserTrainingSerializer(trainings, many=True).data,
            }
        )


class CancelView(APIView):
    """Cancel a training booking."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        training_id = request.data.get("training_id")

        if not training_id:
            return Response(
                {"error": "training_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            training = UserTraining.objects.get(id=training_id, user=request.user)
        except UserTraining.DoesNotExist:
            return Response(
                {"error": "Entrenamiento no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if training.status != UserTraining.Status.CONFIRMED:
            return Response(
                {"error": "Solo puedes cancelar entrenamientos confirmados"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cancel the training
        training.status = UserTraining.Status.CANCELLED
        training.save()

        # Update stats
        now = timezone.localtime()
        current_week = now.isocalendar()[1]

        try:
            stats = UserStats.objects.get(
                user=request.user, week=current_week, year=now.year
            )
            if stats.trainings > 0:
                stats.trainings = F("trainings") - 1
                stats.calories = F("calories") - 400
                stats.hours = F("hours") - 1
                stats.save()
        except UserStats.DoesNotExist:
            pass

        return Response(
            {"success": True, "message": "Entrenamiento cancelado exitosamente"},
            status=status.HTTP_200_OK,
        )


class TrainingTypesView(APIView):
    """Get available training types."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from neural.api.serializers.training import TrainingTypeSerializer

        training_types = TrainingType.objects.all()
        return Response(
            {
                "training_types": TrainingTypeSerializer(
                    training_types, many=True
                ).data,
            }
        )

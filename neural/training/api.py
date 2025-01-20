"""Api training."""

import logging

# Django
from django.utils import timezone
from datetime import timedelta

# Django REST Framework
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Models
from neural.training.models import Slot, UserTraining
from neural.users.models import UserPaymentReference

# Serializers
from neural.training.serializers import SlotModelSerializer, SeatModelSerializer

logger = logging.getLogger(__name__)


class TrainingViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def get_slots(self, request):
        now = timezone.localtime()
        now_date = timezone.localdate()
        gap_acceptance = now + timedelta(minutes=20)
        date = request.data.get("date")
        training_type = request.data.get("training_type")
        if date == now_date.strftime("%Y-%m-%d"):
            slots = (
                Slot.objects.filter(
                    date=date,
                    training_type=training_type,
                    hour_init__gte=gap_acceptance,
                )
                .order_by("hour_init")
                .distinct("hour_init")
            )
        else:
            slots = (
                Slot.objects.filter(date=date, training_type=training_type)
                .order_by("hour_init")
                .distinct("hour_init")
            )
        if slots:
            data = SlotModelSerializer(slots, many=True).data
        else:
            data = "No data"
        return Response({"result": data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def get_seats(self, request):
        slot = request.data.get("slot")
        slot = Slot.objects.get(pk=slot)
        if slot.available_places:
            available_seats = slot.available_seats
            data = SeatModelSerializer(available_seats, many=True).data
        else:
            data = "No data"
        return Response({"result": data}, status=status.HTTP_200_OK)

    def _update_stats(self, user, slot):
        try:
            year = timezone.now().year
            slot_week_number = slot.date.isocalendar()[1]
            stats = user.stats.filter(
                year=year,
                week=slot_week_number,
            ).last()
            if stats:
                if stats.trainings > 0:
                    stats.trainings -= 1
                if stats.calories > 0:
                    stats.calories -= 400
                if stats.hours > 0:
                    stats.hours -= 1
                stats.save()

            # Check streak to decrease it, if not have another training in the week
            streak = user.strikes.filter(
                is_current=True, last_week=slot_week_number
            ).first()
            if streak:
                # Check other training in the week
                trainings_in_week = UserTraining.objects.filter(
                    user=user,
                    slot__date__week=slot_week_number,
                    slot__date__year=year,
                    status=UserTraining.Status.CONFIRMED,
                ).exists()
                if not trainings_in_week:
                    if streak.weeks > 0:
                        streak.weeks -= 1
                    if streak.last_week > 0:
                        streak.last_week -= 1
                    streak.save()
        except Exception as e:
            logger.error(f"Error updating stats: {e}")

    @action(detail=False, methods=["post"])
    def cancel_session(self, request):
        user_training = request.data.get("user_training")
        training = UserTraining.objects.get(pk=user_training)
        training.status = UserTraining.Status.CANCELLED
        training.space = None
        training.save()
        self._update_stats(training.user, training.slot)
        return Response({"result": "OK"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post", "get"], url_path="hook")
    def hook(self, request):
        reference = request.data.get("data", {}).get("metadata", {}).get("reference")
        payment = UserPaymentReference.objects.filter(reference=reference).last()
        if payment:
            logger.info(f"Payment received: {payment}")
            payment.data = request.data
            payment.save()
            if not payment.is_paid:
                payment.apply_membership()
        return Response({"result": "OK"}, status=status.HTTP_200_OK)

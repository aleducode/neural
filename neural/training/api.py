"""Api training."""

# Django
from django.utils import timezone
from datetime import timedelta

# Django REST Framework
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

# Models
from neural.training.models import Slot

# Serializers
from neural.training.serializers import SlotModelSerializer


class TrainingViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def get_slots(self, request):
        now = timezone.localtime()
        gap_acceptance = now + timedelta(minutes=20)
        date = request.data.get('date')
        slots = Slot.objects.filter(date=date, hour_init__gte=gap_acceptance).order_by('hour_init').distinct('hour_init')
        if slots:
            data = SlotModelSerializer(slots, many=True).data
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_404_NOT_FOUND
            data = 'No data'
        return Response({'result': data}, status=status_code)

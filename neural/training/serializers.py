"""Training Serializers."""

# Django Rest Framework
from rest_framework import serializers

# Model
from neural.training.models import Slot


class SlotModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slot
        fields = (
            'id',
            'date',
            'hour_init',
            'hour_end',
            'max_places',
            'training_type',
            'available_places'
        )

    hour_init = serializers.TimeField(format="%I:%M %p")
    hour_end = serializers.TimeField(format="%I:%M %p")

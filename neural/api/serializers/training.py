"""Training serializers for API v1."""

from rest_framework import serializers

from neural.training.models import Slot, UserTraining, TrainingType


class TrainingTypeSerializer(serializers.ModelSerializer):
    """Training type serializer."""

    class Meta:
        model = TrainingType
        fields = ["id", "name", "slug_name", "is_group"]


class SlotSerializer(serializers.ModelSerializer):
    """Slot serializer for API responses."""

    hour_init = serializers.SerializerMethodField()
    hour_end = serializers.SerializerMethodField()
    training_type = serializers.SerializerMethodField()
    available_places = serializers.IntegerField(read_only=True)

    class Meta:
        model = Slot
        fields = [
            "id",
            "date",
            "hour_init",
            "hour_end",
            "max_places",
            "available_places",
            "training_type",
        ]

    def get_hour_init(self, obj):
        if obj.class_training:
            return obj.class_training.hour_init.strftime("%I:%M %p")
        return None

    def get_hour_end(self, obj):
        if obj.class_training:
            return obj.class_training.hour_end.strftime("%I:%M %p")
        return None

    def get_training_type(self, obj):
        if obj.class_training and obj.class_training.training_type:
            return TrainingTypeSerializer(obj.class_training.training_type).data
        return None


class CalendarDaySerializer(serializers.Serializer):
    """Calendar day serializer."""

    date = serializers.DateField()
    day_name = serializers.CharField()
    has_slots = serializers.BooleanField()


class UserTrainingSerializer(serializers.ModelSerializer):
    """User training serializer for API responses."""

    slot = SlotSerializer(read_only=True)
    training_type = serializers.SerializerMethodField()
    is_today = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = UserTraining
        fields = [
            "id",
            "slot",
            "training_type",
            "status",
            "is_today",
            "can_cancel",
        ]

    def get_training_type(self, obj):
        if obj.slot and obj.slot.class_training:
            return TrainingTypeSerializer(
                obj.slot.class_training.training_type
            ).data
        return None

    def get_is_today(self, obj):
        return obj.is_now

    def get_can_cancel(self, obj):
        # Can cancel if status is CONFIRMED and not today
        return obj.status == UserTraining.Status.CONFIRMED


class BookingSerializer(serializers.Serializer):
    """Serializer for booking a slot."""

    slot_id = serializers.IntegerField()

    def validate_slot_id(self, value):
        try:
            slot = Slot.objects.get(id=value)
        except Slot.DoesNotExist:
            raise serializers.ValidationError("Slot no encontrado")

        if slot.available_places <= 0:
            raise serializers.ValidationError(
                "Este horario ya no tiene cupo disponible"
            )

        return value


class CancelSerializer(serializers.Serializer):
    """Serializer for canceling a training."""

    training_id = serializers.IntegerField()

    def validate_training_id(self, value):
        user = self.context.get("user")
        try:
            training = UserTraining.objects.get(id=value, user=user)
        except UserTraining.DoesNotExist:
            raise serializers.ValidationError("Entrenamiento no encontrado")

        if training.status != UserTraining.Status.CONFIRMED:
            raise serializers.ValidationError(
                "Solo puedes cancelar entrenamientos confirmados"
            )

        return value

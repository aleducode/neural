"""Membership serializers for API v1."""

from rest_framework import serializers

from neural.users.models import NeuralPlan, UserMembership


class NeuralPlanSerializer(serializers.ModelSerializer):
    """Neural plan serializer."""

    price = serializers.SerializerMethodField()

    class Meta:
        model = NeuralPlan
        fields = [
            "id",
            "name",
            "slug_name",
            "description",
            "price",
            "duration",
        ]

    def get_price(self, obj):
        return obj.raw_price


class UserMembershipSerializer(serializers.ModelSerializer):
    """User membership serializer."""

    plan = NeuralPlanSerializer(read_only=True)
    days_left = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserMembership
        fields = [
            "id",
            "membership_type",
            "plan",
            "is_active",
            "init_date",
            "expiration_date",
            "days_left",
        ]


class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating a payment."""

    plan_id = serializers.IntegerField()

    def validate_plan_id(self, value):
        try:
            NeuralPlan.objects.get(id=value)
        except NeuralPlan.DoesNotExist:
            raise serializers.ValidationError("Plan no encontrado")
        return value


class VerifyPaymentSerializer(serializers.Serializer):
    """Serializer for verifying a payment."""

    order_id = serializers.CharField()
    tx_status = serializers.CharField()

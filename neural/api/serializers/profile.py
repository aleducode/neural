"""Profile serializers for API v1."""

from datetime import date
from rest_framework import serializers

from neural.users.models import Profile, UserWeight


class ProfileSerializer(serializers.ModelSerializer):
    """Profile serializer."""

    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "height",
            "birthdate",
            "age",
            "address",
            "emergency_contact",
            "emergency_contact_phone",
            "profession",
            "instagram",
        ]
        read_only_fields = ["id", "age"]

    def get_age(self, obj):
        if obj.birthdate:
            today = date.today()
            age = today.year - obj.birthdate.year
            # Check if birthday has passed this year
            if (today.month, today.day) < (obj.birthdate.month, obj.birthdate.day):
                age -= 1
            return age
        return None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile."""

    class Meta:
        model = Profile
        fields = [
            "height",
            "birthdate",
            "address",
            "emergency_contact",
            "emergency_contact_phone",
            "profession",
            "instagram",
        ]


class UserWeightSerializer(serializers.ModelSerializer):
    """User weight serializer."""

    date = serializers.SerializerMethodField()

    class Meta:
        model = UserWeight
        fields = [
            "id",
            "weight",
            "date",
            "created",
        ]
        read_only_fields = ["id", "date", "created"]

    def get_date(self, obj):
        return obj.created.date().isoformat() if obj.created else None


class CreateWeightSerializer(serializers.Serializer):
    """Serializer for creating a weight entry."""

    weight = serializers.IntegerField(min_value=20, max_value=300)

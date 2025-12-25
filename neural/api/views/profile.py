"""Profile views for API v1."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.api.serializers.profile import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    UserWeightSerializer,
    CreateWeightSerializer,
)
from neural.users.models import Profile, UserWeight


class ProfileView(APIView):
    """Get and update user profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user, defaults={"plan": None}
        )

        # Get latest weight
        latest_weight = (
            UserWeight.objects.filter(user=request.user).order_by("-created").first()
        )

        return Response(
            {
                "profile": ProfileSerializer(profile).data,
                "latest_weight": UserWeightSerializer(latest_weight).data
                if latest_weight
                else None,
            }
        )

    def patch(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user, defaults={"plan": None}
        )

        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "profile": ProfileSerializer(profile).data,
            }
        )


class WeightListView(APIView):
    """List user weight history."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        weights = UserWeight.objects.filter(user=request.user).order_by("-created")[
            :30
        ]  # Last 30 entries

        # Calculate stats
        all_weights = list(weights)

        stats = {
            "current": all_weights[0].weight if all_weights else None,
            "min": min(w.weight for w in all_weights) if all_weights else None,
            "max": max(w.weight for w in all_weights) if all_weights else None,
            "total_entries": len(all_weights),
        }

        # Calculate change from first to last
        if len(all_weights) >= 2:
            stats["change"] = all_weights[0].weight - all_weights[-1].weight
        else:
            stats["change"] = 0

        return Response(
            {
                "weights": UserWeightSerializer(weights, many=True).data,
                "stats": stats,
            }
        )


class WeightCreateView(APIView):
    """Create a new weight entry."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateWeightSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        weight = UserWeight.objects.create(
            user=request.user,
            weight=serializer.validated_data["weight"],
        )

        return Response(
            {
                "weight": UserWeightSerializer(weight).data,
                "message": "Peso registrado exitosamente",
            },
            status=status.HTTP_201_CREATED,
        )

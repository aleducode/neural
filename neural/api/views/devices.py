"""Device views for push notifications."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from neural.users.models import Device


class RegisterDeviceView(APIView):
    """Register a device for push notifications."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")
        platform = request.data.get("platform")
        device_id = request.data.get("device_id")

        if not all([token, platform, device_id]):
            return Response(
                {"error": "token, platform y device_id son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if platform not in ["ios", "android"]:
            return Response(
                {"error": "platform debe ser 'ios' o 'android'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update or create device
        device, created = Device.objects.update_or_create(
            device_id=device_id,
            defaults={
                "user": request.user,
                "token": token,
                "platform": platform,
                "is_active": True,
            },
        )

        return Response(
            {
                "success": True,
                "message": "Dispositivo registrado exitosamente",
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UnregisterDeviceView(APIView):
    """Unregister a device from push notifications."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        device_id = request.data.get("device_id")

        if not device_id:
            return Response(
                {"error": "device_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device = Device.objects.get(
                device_id=device_id, user=request.user
            )
            device.is_active = False
            device.save()

            return Response(
                {"success": True, "message": "Dispositivo eliminado"},
                status=status.HTTP_200_OK,
            )
        except Device.DoesNotExist:
            return Response(
                {"error": "Dispositivo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

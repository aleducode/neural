"""Notification views for API v1."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from neural.users.models import PushNotification, User
from neural.api.serializers.notifications import (
    NotificationSerializer,
    NotificationDetailSerializer,
    SendNotificationSerializer,
)
from neural.services.push_notifications import (
    PushNotificationService,
    NotificationPayload,
)


class NotificationListView(APIView):
    """List user notifications."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all notifications for the current user."""
        # Include PENDING, SENT, DELIVERED, and READ notifications
        # Exclude FAILED notifications
        notifications = PushNotification.objects.filter(
            user=request.user,
            status__in=[
                PushNotification.Status.PENDING,
                PushNotification.Status.SENT,
                PushNotification.Status.DELIVERED,
                PushNotification.Status.READ,
            ],
        ).order_by("-created")[:50]  # Last 50 notifications

        serializer = NotificationSerializer(notifications, many=True)

        # Get unread count (PENDING, SENT, DELIVERED are considered unread)
        unread_count = PushNotification.objects.filter(
            user=request.user,
            status__in=[
                PushNotification.Status.PENDING,
                PushNotification.Status.SENT,
                PushNotification.Status.DELIVERED,
            ],
        ).count()

        return Response(
            {
                "notifications": serializer.data,
                "unread_count": unread_count,
            }
        )


class NotificationDetailView(APIView):
    """Get single notification details."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get a specific notification."""
        try:
            notification = PushNotification.objects.get(
                pk=pk,
                user=request.user,
            )
        except PushNotification.DoesNotExist:
            return Response(
                {"error": "Notificación no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NotificationDetailSerializer(notification)
        return Response(serializer.data)

    def delete(self, request, pk):
        """Delete a notification."""
        try:
            notification = PushNotification.objects.get(
                pk=pk,
                user=request.user,
            )
        except PushNotification.DoesNotExist:
            return Response(
                {"error": "Notificación no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkNotificationReadView(APIView):
    """Mark notification(s) as read."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        """Mark a specific notification as read."""
        if pk:
            # Mark single notification as read
            try:
                notification = PushNotification.objects.get(
                    pk=pk,
                    user=request.user,
                )
            except PushNotification.DoesNotExist:
                return Response(
                    {"error": "Notificación no encontrada"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            notification.mark_as_read()
            return Response({"message": "Notificación marcada como leída"})
        else:
            # Mark all notifications as read
            PushNotification.objects.filter(
                user=request.user,
                status__in=[
                    PushNotification.Status.PENDING,
                    PushNotification.Status.SENT,
                    PushNotification.Status.DELIVERED,
                ],
            ).update(
                status=PushNotification.Status.READ,
                read_at=timezone.now(),
            )
            return Response(
                {"message": "Todas las notificaciones marcadas como leídas"}
            )


class NotificationCountView(APIView):
    """Get notification counts."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get notification counts."""
        total = PushNotification.objects.filter(
            user=request.user,
            status__in=[
                PushNotification.Status.PENDING,
                PushNotification.Status.SENT,
                PushNotification.Status.DELIVERED,
                PushNotification.Status.READ,
            ],
        ).count()

        unread = PushNotification.objects.filter(
            user=request.user,
            status__in=[
                PushNotification.Status.PENDING,
                PushNotification.Status.SENT,
                PushNotification.Status.DELIVERED,
            ],
        ).count()

        return Response(
            {
                "total": total,
                "unread": unread,
            }
        )


class SendNotificationView(APIView):
    """Admin endpoint to send notifications."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        """Send a notification to user(s)."""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        payload = NotificationPayload(
            title=data["title"],
            body=data["body"],
            notification_type=data["notification_type"],
            data=data.get("data"),
        )

        if data.get("send_to_all"):
            # Send to all users
            count = PushNotificationService.send_to_all_users(payload)
            return Response(
                {
                    "message": f"Notificación enviada a {count} usuarios",
                    "count": count,
                }
            )
        elif data.get("user_id"):
            # Send to specific user
            try:
                user = User.objects.get(pk=data["user_id"])
            except User.DoesNotExist:
                return Response(
                    {"error": "Usuario no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            notification = PushNotificationService.send_to_user(user, payload)
            if notification:
                return Response(
                    {
                        "message": "Notificación enviada",
                        "notification_id": notification.id,
                    }
                )
            else:
                return Response(
                    {"error": "El usuario no tiene dispositivos activos"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "Debe especificar user_id o send_to_all"},
                status=status.HTTP_400_BAD_REQUEST,
            )

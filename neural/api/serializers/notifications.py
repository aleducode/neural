"""Notification serializers for API v1."""

from rest_framework import serializers
from django.utils import timezone

from neural.users.models import PushNotification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications list."""

    time_ago = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = PushNotification
        fields = [
            "id",
            "title",
            "body",
            "notification_type",
            "status",
            "data",
            "created",
            "read_at",
            "time_ago",
            "is_read",
        ]
        read_only_fields = fields

    def get_time_ago(self, obj) -> str:
        """Get human-readable time ago string."""
        now = timezone.now()
        diff = now - obj.created

        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if seconds < 60:
            return "Ahora"
        elif minutes < 60:
            mins = int(minutes)
            return f"Hace {mins} min"
        elif hours < 24:
            hrs = int(hours)
            return f"Hace {hrs}h"
        elif days < 7:
            d = int(days)
            return f"Hace {d} día{'s' if d > 1 else ''}"
        else:
            return obj.created.strftime("%d/%m/%Y")

    def get_is_read(self, obj) -> bool:
        return obj.status == PushNotification.Status.READ


class NotificationDetailSerializer(NotificationSerializer):
    """Detailed serializer for a single notification."""

    class Meta(NotificationSerializer.Meta):
        fields = NotificationSerializer.Meta.fields + ["sent_at"]


class MarkNotificationReadSerializer(serializers.Serializer):
    """Serializer for marking notification as read."""

    notification_id = serializers.IntegerField(required=False)


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for admin sending notifications."""

    user_id = serializers.IntegerField(required=False, help_text="Specific user ID")
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=PushNotification.NotificationType.choices,
        default=PushNotification.NotificationType.GENERAL,
    )
    data = serializers.JSONField(required=False, default=dict)
    send_to_all = serializers.BooleanField(default=False, help_text="Send to all users")


class NotificationCountSerializer(serializers.Serializer):
    """Serializer for notification counts."""

    total = serializers.IntegerField()
    unread = serializers.IntegerField()

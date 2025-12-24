"""Push Notification Service for Expo Push API."""

import logging
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from django.utils import timezone

from neural.users.models import (
    User,
    Device,
    PushNotification,
    PushNotificationLog,
)

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
EXPO_RECEIPTS_URL = "https://exp.host/--/api/v2/push/getReceipts"


@dataclass
class NotificationPayload:
    """Payload for a push notification."""
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    notification_type: str = PushNotification.NotificationType.GENERAL
    sound: str = "default"
    badge: Optional[int] = None
    channel_id: str = "default"


class PushNotificationService:
    """Service for sending push notifications via Expo Push API."""

    @classmethod
    def send_to_user(
        cls,
        user: User,
        payload: NotificationPayload,
        save_notification: bool = True,
    ) -> Optional[PushNotification]:
        """
        Send a push notification to all active devices of a user.

        Args:
            user: The user to send the notification to
            payload: The notification payload
            save_notification: Whether to save the notification to the database

        Returns:
            The created PushNotification object or None if no devices found
        """
        devices = Device.objects.filter(user=user, is_active=True)

        if not devices.exists():
            logger.warning(f"No active devices found for user {user.id}")
            return None

        # Create the notification record
        notification = None
        if save_notification:
            notification = PushNotification.objects.create(
                user=user,
                title=payload.title,
                body=payload.body,
                data=payload.data,
                notification_type=payload.notification_type,
                status=PushNotification.Status.PENDING,
            )

        # Send to all devices
        success_count = 0
        for device in devices:
            success = cls._send_to_device(
                device=device,
                payload=payload,
                notification=notification,
            )
            if success:
                success_count += 1

        # Update notification status
        if notification:
            if success_count > 0:
                notification.status = PushNotification.Status.SENT
                notification.sent_at = timezone.now()
            else:
                notification.status = PushNotification.Status.FAILED
            notification.save()

        return notification

    @classmethod
    def send_to_users(
        cls,
        users: List[User],
        payload: NotificationPayload,
    ) -> List[PushNotification]:
        """
        Send a push notification to multiple users.

        Args:
            users: List of users to send the notification to
            payload: The notification payload

        Returns:
            List of created PushNotification objects
        """
        notifications = []
        for user in users:
            notification = cls.send_to_user(user, payload)
            if notification:
                notifications.append(notification)
        return notifications

    @classmethod
    def send_to_all_users(
        cls,
        payload: NotificationPayload,
        exclude_users: Optional[List[int]] = None,
    ) -> int:
        """
        Send a push notification to all users with active devices.

        Args:
            payload: The notification payload
            exclude_users: List of user IDs to exclude

        Returns:
            Number of notifications sent
        """
        users_with_devices = User.objects.filter(
            devices__is_active=True
        ).distinct()

        if exclude_users:
            users_with_devices = users_with_devices.exclude(id__in=exclude_users)

        count = 0
        for user in users_with_devices:
            notification = cls.send_to_user(user, payload)
            if notification:
                count += 1

        return count

    @classmethod
    def _send_to_device(
        cls,
        device: Device,
        payload: NotificationPayload,
        notification: Optional[PushNotification] = None,
    ) -> bool:
        """
        Send a push notification to a specific device.

        Args:
            device: The device to send the notification to
            payload: The notification payload
            notification: The associated notification record (for logging)

        Returns:
            True if sent successfully, False otherwise
        """
        # Build the Expo push message
        message = {
            "to": device.token,
            "title": payload.title,
            "body": payload.body,
            "sound": payload.sound,
            "channelId": payload.channel_id,
        }

        if payload.data:
            message["data"] = payload.data

        if payload.badge is not None:
            message["badge"] = payload.badge

        # Add notification ID to data for tracking
        if notification:
            if "data" not in message:
                message["data"] = {}
            message["data"]["notification_id"] = notification.id

        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=[message],
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )

            response_data = response.json()

            # Log the request/response
            log_status = PushNotificationLog.Status.SUCCESS
            error_message = None
            expo_receipt_id = None

            if response.status_code == 200 and "data" in response_data:
                ticket = response_data["data"][0]
                if ticket.get("status") == "ok":
                    expo_receipt_id = ticket.get("id")
                else:
                    log_status = PushNotificationLog.Status.ERROR
                    error_message = ticket.get("message", "Unknown error")

                    # Handle invalid token
                    if ticket.get("details", {}).get("error") == "DeviceNotRegistered":
                        device.is_active = False
                        device.save()
                        logger.info(f"Deactivated device {device.id} - not registered")
            else:
                log_status = PushNotificationLog.Status.ERROR
                error_message = response_data.get("error", "HTTP error")

            # Save log
            if notification:
                PushNotificationLog.objects.create(
                    notification=notification,
                    device=device,
                    expo_push_token=device.token,
                    request_payload=message,
                    response_payload=response_data,
                    status=log_status,
                    expo_receipt_id=expo_receipt_id,
                    error_message=error_message,
                )

            return log_status == PushNotificationLog.Status.SUCCESS

        except requests.RequestException as e:
            logger.error(f"Error sending push notification: {e}")

            if notification:
                PushNotificationLog.objects.create(
                    notification=notification,
                    device=device,
                    expo_push_token=device.token,
                    request_payload=message,
                    response_payload=None,
                    status=PushNotificationLog.Status.ERROR,
                    error_message=str(e),
                )

            return False

    @classmethod
    def send_training_reminder(
        cls,
        user: User,
        training_type: str,
        time: str,
    ) -> Optional[PushNotification]:
        """Send a training reminder notification."""
        payload = NotificationPayload(
            title="Recordatorio de entrenamiento",
            body=f"Tu clase de {training_type} comienza a las {time}. ¡No llegues tarde!",
            notification_type=PushNotification.NotificationType.TRAINING_REMINDER,
            data={"type": "training_reminder"},
        )
        return cls.send_to_user(user, payload)

    @classmethod
    def send_training_cancelled(
        cls,
        user: User,
        training_type: str,
        date: str,
    ) -> Optional[PushNotification]:
        """Send a training cancellation notification."""
        payload = NotificationPayload(
            title="Entrenamiento cancelado",
            body=f"Tu clase de {training_type} del {date} ha sido cancelada.",
            notification_type=PushNotification.NotificationType.TRAINING_CANCELLED,
            data={"type": "training_cancelled"},
        )
        return cls.send_to_user(user, payload)

    @classmethod
    def send_membership_expiring(
        cls,
        user: User,
        days_left: int,
    ) -> Optional[PushNotification]:
        """Send a membership expiring notification."""
        if days_left == 1:
            body = "Tu membresía vence mañana. ¡Renuévala para seguir entrenando!"
        else:
            body = f"Tu membresía vence en {days_left} días. ¡Renuévala pronto!"

        payload = NotificationPayload(
            title="Membresía por vencer",
            body=body,
            notification_type=PushNotification.NotificationType.MEMBERSHIP_EXPIRING,
            data={"type": "membership_expiring", "days_left": days_left},
        )
        return cls.send_to_user(user, payload)

    @classmethod
    def send_membership_expired(
        cls,
        user: User,
    ) -> Optional[PushNotification]:
        """Send a membership expired notification."""
        payload = NotificationPayload(
            title="Membresía vencida",
            body="Tu membresía ha vencido. Renuévala para continuar con tus entrenamientos.",
            notification_type=PushNotification.NotificationType.MEMBERSHIP_EXPIRED,
            data={"type": "membership_expired"},
        )
        return cls.send_to_user(user, payload)

    @classmethod
    def send_achievement(
        cls,
        user: User,
        achievement_title: str,
        achievement_description: str,
    ) -> Optional[PushNotification]:
        """Send an achievement unlocked notification."""
        payload = NotificationPayload(
            title=f"¡{achievement_title}!",
            body=achievement_description,
            notification_type=PushNotification.NotificationType.ACHIEVEMENT,
            data={"type": "achievement"},
        )
        return cls.send_to_user(user, payload)

    @classmethod
    def check_receipts(cls, receipt_ids: List[str]) -> Dict[str, Any]:
        """
        Check the delivery status of sent notifications.

        Args:
            receipt_ids: List of Expo receipt IDs

        Returns:
            Dictionary with receipt statuses
        """
        try:
            response = requests.post(
                EXPO_RECEIPTS_URL,
                json={"ids": receipt_ids},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=10,
            )
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error checking receipts: {e}")
            return {}

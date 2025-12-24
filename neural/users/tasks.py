# Celery
from config import celery_app
from celery.schedules import crontab
from django.utils import timezone
from datetime import timedelta
import logging

# Models
from neural.users.models import UserMembership

# Services
from neural.services.push_notifications import PushNotificationService

logger = logging.getLogger(__name__)


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # Check expired memberships - daily at midnight
    sender.add_periodic_task(
        crontab(day_of_week="*", hour=0, minute=0),
        check_user_memberships.s(),
        name="check_user_memberships",
    )

    # Send membership expiring reminders - daily at 10am
    sender.add_periodic_task(
        crontab(day_of_week="*", hour=10, minute=0),
        send_membership_expiring_notifications.s(),
        name="send_membership_expiring_notifications",
    )

    # Send training reminders - every 30 minutes
    sender.add_periodic_task(
        crontab(minute="*/30"),
        send_training_reminders.s(),
        name="send_training_reminders",
    )


@celery_app.task
def check_user_memberships():
    """Check and expire user memberships, send notification."""
    today = timezone.localdate()
    user_memberships = UserMembership.objects.filter(
        is_active=True, expiration_date__lt=today
    )

    for membership in user_memberships:
        membership.is_active = False
        membership.save()

        # Send expired notification
        try:
            PushNotificationService.send_membership_expired(membership.user)
            logger.info(
                f"Sent membership expired notification to {membership.user.email}"
            )
        except Exception as e:
            logger.error(f"Error sending membership expired notification: {e}")


@celery_app.task
def send_membership_expiring_notifications():
    """Send notifications for memberships expiring in 3 days and 1 day."""
    today = timezone.localdate()

    # Check memberships expiring in 3 days
    expiring_3_days = today + timedelta(days=3)
    memberships_3_days = UserMembership.objects.filter(
        is_active=True, expiration_date=expiring_3_days
    )

    for membership in memberships_3_days:
        try:
            PushNotificationService.send_membership_expiring(
                membership.user, days_left=3
            )
            logger.info(f"Sent 3-day expiring notification to {membership.user.email}")
        except Exception as e:
            logger.error(f"Error sending 3-day expiring notification: {e}")

    # Check memberships expiring tomorrow
    expiring_1_day = today + timedelta(days=1)
    memberships_1_day = UserMembership.objects.filter(
        is_active=True, expiration_date=expiring_1_day
    )

    for membership in memberships_1_day:
        try:
            PushNotificationService.send_membership_expiring(
                membership.user, days_left=1
            )
            logger.info(f"Sent 1-day expiring notification to {membership.user.email}")
        except Exception as e:
            logger.error(f"Error sending 1-day expiring notification: {e}")


@celery_app.task
def send_training_reminders():
    """Send reminders for trainings starting in 1 hour."""
    from neural.training.models import UserTraining, Slot

    now = timezone.localtime()
    today = now.date()
    (now + timedelta(hours=1)).time()

    # Find slots for today where the training starts within the next hour
    # We check for trainings starting between now+55min and now+65min
    time_start = (now + timedelta(minutes=55)).time()
    time_end = (now + timedelta(minutes=65)).time()

    # Get slots for today
    slots = Slot.objects.filter(
        date=today,
        class_training__hour_init__gte=time_start,
        class_training__hour_init__lte=time_end,
    ).select_related("class_training", "class_training__training_type")

    for slot in slots:
        # Get confirmed trainings for this slot
        user_trainings = UserTraining.objects.filter(
            slot=slot,
            status=UserTraining.Status.CONFIRMED,
        ).select_related("user")

        for training in user_trainings:
            try:
                training_type = slot.class_training.training_type.name
                time_str = slot.class_training.hour_init.strftime("%H:%M")

                PushNotificationService.send_training_reminder(
                    user=training.user,
                    training_type=training_type,
                    time=time_str,
                )
                logger.info(
                    f"Sent training reminder to {training.user.email} for {training_type} at {time_str}"
                )
            except Exception as e:
                logger.error(f"Error sending training reminder: {e}")


@celery_app.task
def send_push_notification_to_user(
    user_id: int, title: str, body: str, notification_type: str = "general"
):
    """
    Generic task to send a push notification to a specific user.
    Can be called from anywhere in the codebase.
    """
    from neural.users.models import User
    from neural.services.push_notifications import NotificationPayload

    try:
        user = User.objects.get(pk=user_id)
        payload = NotificationPayload(
            title=title,
            body=body,
            notification_type=notification_type,
        )
        notification = PushNotificationService.send_to_user(user, payload)
        if notification:
            logger.info(f"Sent notification to user {user_id}: {title}")
            return notification.id
        else:
            logger.warning(f"No devices found for user {user_id}")
            return None
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")
        return None


@celery_app.task
def send_push_notification_to_all(
    title: str, body: str, notification_type: str = "general"
):
    """
    Task to send a push notification to all users with active devices.
    """
    from neural.services.push_notifications import NotificationPayload

    try:
        payload = NotificationPayload(
            title=title,
            body=body,
            notification_type=notification_type,
        )
        count = PushNotificationService.send_to_all_users(payload)
        logger.info(f"Sent notification to {count} users: {title}")
        return count
    except Exception as e:
        logger.error(f"Error sending notification to all users: {e}")
        return 0

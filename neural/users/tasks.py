# Celery
from config import celery_app
from celery.schedules import crontab
from django.utils import timezone

# Models
from neural.users.models import UserMembership


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(day_of_week="*", hour=00, minute=00),
        check_user_memberships,
        name="check_user_memberships",
    )


@celery_app.task
def check_user_memberships():
    """Check user memberships"""
    user_memberships = UserMembership.objects.filter(
        is_active=True, expiration_date=timezone.localdate()
    )
    for membership in user_memberships:
        membership.is_active = False
        membership.save()

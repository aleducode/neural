from datetime import datetime, timedelta

# Celery
from config import celery_app
from celery.schedules import crontab

# Models
from neural.training.models import Classes, Slot


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(day_of_week="*", hour=00, minute=00),
        create_schedule_day,
        name="create_schedule_day",
    )


@celery_app.task
def create_schedule_day():
    """Create slot available with delta 7 days"""
    wrapper_days = {
        0: "MONDAY",
        1: "TUESDAY",
        2: "WEDNESDAY",
        3: "THURSDAY",
        4: "FRIDAY",
        5: "SATURDAY",
        6: "SUNDAY",
    }
    now = datetime.now().date()
    delta_day = now + timedelta(days=7)
    day_name = wrapper_days.get(delta_day.weekday())
    classes = Classes.objects.filter(day=day_name)
    for session in classes:
        Slot.objects.update_or_create(
            date=delta_day, class_trainging=session, defaults={"max_places": 20}
        )
    print("Finish")

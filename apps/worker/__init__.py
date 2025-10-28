from apps.worker.app import celery
from apps.worker.tasks import (
    send_notification,
    example_db_task,
    send_listing_notification,
    run_ingest,
)
from apps.worker.schedules import beat_schedule

celery.conf.beat_schedule = beat_schedule


__all__ = [
    "celery",
    "send_notification",
    "example_db_task",
    "send_listing_notification",
    "run_ingest",
]

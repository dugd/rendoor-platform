from apps.worker.app import celery
from apps.worker.tasks import (
    example_db_task,
    run_ingest,
    send_notification,
    process_outbox,
    match_listing_with_subscriptions,
)
from apps.worker.schedules import beat_schedule

celery.autodiscover_tasks(["apps.worker.tasks"])
celery.conf.beat_schedule = beat_schedule

__all__ = [
    "celery",
    "example_db_task",
    "run_ingest",
    "send_notification",
    "process_outbox",
    "match_listing_with_subscriptions",
]

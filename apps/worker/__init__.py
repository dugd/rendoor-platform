from apps.worker.app import celery
from apps.worker.tasks import (
    example_db_task,
    run_ingest,
)
from apps.worker.schedules import beat_schedule

celery.conf.beat_schedule = beat_schedule


__all__ = [
    "celery",
    "example_db_task",
    "run_ingest",
]

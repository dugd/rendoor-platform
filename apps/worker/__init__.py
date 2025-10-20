from apps.worker.app import celery
from apps.worker.schedules import beat_schedule

celery.conf.beat_schedule = beat_schedule


__all__ = ("celery",)

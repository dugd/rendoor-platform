from celery import Celery

from src.core.config import get_settings

settings = get_settings()

celery = Celery(
    "job",
    broker=settings.BROKER_URL,
    worker_hijack_root_logger=False,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="Europe/Kyiv",
    enable_utc=True,
)

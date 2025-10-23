import os
import asyncio

from loguru import logger
from celery import Celery, signals

from core.config import get_settings
from core.infra.telemetry.logger import setup_loguru
from core.infra.db import init_db, shutdown_db
from .di import get_container


settings = get_settings()

setup_loguru(
    service=os.environ.get("APP_SERVICE_NAME", "celery-app"),
    level=get_settings().LOGGING_LEVEL,
    sink="text",  # TODO: switch via env
    settings={
        "backtrace": True,
        "enqueue": True,
        "diagnose": True,
    }
    if get_settings().DEBUG
    else {
        "backtrace": False,
        "enqueue": True,
        "diagnose": False,
    },
)

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


@signals.setup_logging.connect
def _celery_setup_logging(**kwargs):
    setup_loguru(
        service=os.environ.get("SERVICE_NAME", "celery-app"),
        level=settings.LOGGING_LEVEL,
    )


@signals.worker_process_init.connect
def _celery_worker_process_init(**kwargs):
    """Initialize resources per worker process"""
    setup_loguru(
        service=os.environ.get("SERVICE_NAME", "celery-app"),
        level=settings.LOGGING_LEVEL,
    )
    init_db(dsn=settings.get_postgres_dsn("asyncpg"), echo=settings.DEBUG)

    container = get_container()
    container.get_or_create_loop()
    logger.info("Container initialized for worker process")


@signals.worker_shutdown.connect
def _celery_worker_process_shutdown(**kwargs):
    """Cleanup resources when worker shuts down"""
    from .di import get_container

    async def cleanup():
        await shutdown_db()
        container = get_container()
        container.cleanup()
        logger.info("Container cleaned up")

    asyncio.run(cleanup())


@signals.task_prerun.connect
def on_task_start(sender=None, task_id=None, **_):
    logger.bind(task_id=task_id, task_name=sender.name).info("Task start")


@signals.task_postrun.connect
def on_task_end(sender=None, task_id=None, state=None, **_):
    logger.bind(task_id=task_id, task_name=sender.name, state=state).info("Task end")


@signals.task_failure.connect
def on_task_fail(sender=None, task_id=None, **kw):
    logger.bind(task_id=task_id, task_name=sender.name).exception("Task failed")


__all__ = ["celery"]

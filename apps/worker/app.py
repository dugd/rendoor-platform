import asyncio

from loguru import logger
from celery import Celery, signals

from core.config import get_settings
from core.infra.telemetry.logger import configure_logger
from core.infra.db import init_db, shutdown_db
from core.infra.telegram import init_bot, shutdown_bot
from .lifespan import clear_loop


settings = get_settings()

configure_logger("celery-app")

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
    configure_logger("celery-app")


@signals.worker_process_init.connect
def _celery_worker_process_init(**kwargs):
    """Initialize resources per worker process"""
    configure_logger("celery-app")
    init_db(dsn=settings.get_postgres_dsn("asyncpg"))
    init_bot(settings.TELEGRAM_BOT_TOKEN)
    logger.info("Database and Bot initialized for worker process")


@signals.worker_shutdown.connect
def _celery_worker_process_shutdown(**kwargs):
    """Cleanup resources when worker shuts down"""

    async def cleanup():
        await shutdown_db()
        await shutdown_bot()
        clear_loop()

        logger.info("All resources cleaned up")

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

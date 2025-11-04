# worker/celery_app.py
import asyncio
from loguru import logger
from celery import Celery, signals

from core.config import get_settings
from .di import AppContainer

settings = get_settings()
container = AppContainer()  # singleton container

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


# ---------- signals ----------
@signals.setup_logging.connect
def _celery_setup_logging(**_):
    pass


@signals.worker_process_init.connect
def _celery_worker_init(**_):
    async def _start():
        await container.start()
        logger.info("Container started")

    asyncio.run(_start())


@signals.worker_shutdown.connect
def _celery_worker_shutdown(**_):
    async def _stop():
        await container.stop()
        logger.info("Container stopped")

    asyncio.run(_stop())


@signals.task_prerun.connect
def on_task_start(sender=None, task_id=None, **_):
    logger.bind(task_id=task_id, task_name=getattr(sender, "name", None)).info(
        "Task start"
    )


@signals.task_postrun.connect
def on_task_end(sender=None, task_id=None, state=None, **_):
    logger.bind(
        task_id=task_id, task_name=getattr(sender, "name", None), state=state
    ).info("Task end")


@signals.task_failure.connect
def on_task_fail(sender=None, task_id=None, **_):
    logger.bind(task_id=task_id, task_name=getattr(sender, "name", None)).exception(
        "Task failed"
    )


__all__ = ["celery", "container"]

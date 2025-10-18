import os

from loguru import logger
from celery import Celery, signals
from sqlalchemy import text

from src.core.config import get_settings
from src.core.logger import setup_loguru
from src.storage.db import init_db, shutdown_db, get_sessionmaker_with_init

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
        level=get_settings().LOGGING_LEVEL,
    )


@signals.worker_process_init.connect
def _celery_worker_process_init(**kwargs):
    setup_loguru(
        service=os.environ.get("SERVICE_NAME", "celery-app"),
        level=get_settings().app.LOGGING_LEVEL,
    )
    init_db(dsn=get_settings().get_postgres_dsn("asyncpg"), echo=settings.DEBUG)


@signals.worker_shutdown.connect
def _celery_worker_process_shutdown(**kwargs):
    import asyncio

    asyncio.run(shutdown_db())


@signals.task_prerun.connect
def on_task_start(sender=None, task_id=None, **_):
    logger.bind(task_id=task_id, task_name=sender.name).info("Task start")


@signals.task_postrun.connect
def on_task_end(sender=None, task_id=None, state=None, **_):
    logger.bind(task_id=task_id, task_name=sender.name, state=state).info("Task end")


@signals.task_failure.connect
def on_task_fail(sender=None, task_id=None, **kw):
    logger.bind(task_id=task_id, task_name=sender.name).exception("Task failed")


@celery.task(bind=True, name="example_db_task")
def example_db_task(self) -> int:
    logger.info(self.request.id)
    sm = get_sessionmaker_with_init()
    import asyncio

    async def run_query():
        async with sm() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            return value

    return asyncio.run(run_query())

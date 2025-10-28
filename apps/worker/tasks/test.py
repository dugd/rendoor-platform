from loguru import logger
from sqlalchemy import text

from core.infra.db.context import get_sessionmaker_with_init
from ..app import celery


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

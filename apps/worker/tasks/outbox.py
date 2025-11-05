from loguru import logger

from apps.worker.app import celery, container
from apps.worker.lifespan import get_loop
from .matching import match_listing_with_subscriptions


@celery.task(bind=True)
def process_outbox(self, limit: int = 100):
    """Process pending outbox messages and trigger matching"""

    async def _process():
        async with container.uow() as uow:
            messages = await uow.outbox.get_pending(limit=limit)

            for msg in messages:
                try:
                    await uow.outbox.increment_attempts(msg.uuid)

                    # Queue matching task
                    match_listing_with_subscriptions.delay(str(msg.aggregate_id))

                    await uow.outbox.mark_processed(msg.uuid)
                except Exception as e:
                    logger.error(f"Failed to process outbox {msg.uuid}: {e}")

            await uow.commit()

    loop = get_loop()
    return loop.run_until_complete(_process())

from datetime import datetime, timezone

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.db.context import get_session
from ..di import get_container
from ..lifespan import get_loop
from ..app import celery
from .telegram import notify_admin_listing

HANDLERS = {
    "listing.created": notify_admin_listing,
}


async def _claim_batch(session: AsyncSession, batch: int = 100):
    stmt = text("""
               SELECT id, message_type, aggregate_type, aggregate_id, payload
               FROM outbox_messages
               WHERE processed_at IS NULL
               ORDER BY id
                   LIMIT :batch
               """)
    result = await session.execute(stmt, {"batch": batch})
    return [dict(r) for r in result.mappings()]


async def _ack(session: AsyncSession, msg_id: int):
    await session.execute(
        text(
            "UPDATE outbox_messages SET processed_at=:ts WHERE id=:id AND processed_at IS NULL"
        ),
        {"id": msg_id, "ts": datetime.now(timezone.utc)},
    )


async def _nack(session: AsyncSession, msg_id: int):
    await session.execute(
        text(
            "UPDATE outbox_messages SET processing_attempts = processing_attempts + 1 WHERE id=:id"
        ),
        {"id": msg_id},
    )


@celery.task()
def process_outbox(batch: int = 100):
    container = get_container()
    loop = get_loop()

    async def _run():
        async with get_session() as session:
            msgs = await _claim_batch(session, batch)
            if not msgs:
                return []
            for m in msgs:
                handler = HANDLERS.get(m["message_type"])
                if not handler:
                    logger.warning(
                        "No handler for message type {type}", type=m["message_type"]
                    )
                    await _nack(session, m["id"])
                    continue
                try:
                    await handler(container, int(m["aggregate_id"]))
                    logger.info("Processed outbox message {id}", id=m["id"])
                    await _ack(session, m["id"])
                except Exception:
                    logger.exception("Error processing outbox message {id}", id=m["id"])
                    await _nack(session, m["id"])
            await session.commit()
            return msgs

    result = loop.run_until_complete(_run())

    return len(result)

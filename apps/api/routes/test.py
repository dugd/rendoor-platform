from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from apps.api.depends import get_async_session
from apps.worker import (
    send_notification,
    example_db_task,
    send_listing_notification,
    run_ingest,
)

router = APIRouter(
    prefix="",
    tags=["test"],
    responses={404: {"description": "Not found"}},
)


@router.get("/db-ping")
async def db_ping(session: Annotated[AsyncSession, Depends(get_async_session)]):
    result = await session.execute(text("SELECT 1"))
    val = result.scalar()
    return {"ok": bool(val == 1)}


@router.get("/worker-ping")
async def worker_ping():
    example_db_task.delay()
    return {"status": "ok"}


@router.post("/send-message")
async def send_message(message: str):
    send_notification.delay(message)
    return {"status": "message sent"}


@router.post("/send-listing")
async def send_listing(listing_id: int):
    send_listing_notification.delay(listing_id)
    return {"status": "listing notification sent", "listing_id": listing_id}


@router.post("/run-ingest")
async def trigger_ingest():
    task = run_ingest.delay()
    return {"status": "ingest started", "task_id": task.id}


__all__ = [
    "router",
]

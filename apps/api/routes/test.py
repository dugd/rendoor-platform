from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from apps.api.depends import get_async_session
from apps.worker import (
    example_db_task,
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


@router.post("/run-ingest")
async def trigger_ingest():
    task = run_ingest.delay()
    return {"status": "ingest started", "task_id": task.id}


__all__ = [
    "router",
]

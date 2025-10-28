from contextlib import asynccontextmanager
import os
from typing import TypedDict, AsyncIterator

from loguru import logger
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from core.infra.telemetry.logger import configure_logger
from core.config import get_settings
from core.infra.db import init_db, is_db_initialized, shutdown_db

from .routes import core_router, test_router
from .middlewares import AccessLogMiddleware


class AppState(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: async_sessionmaker[AsyncSession]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up API...")

    settings = get_settings()
    init_db(dsn=settings.get_postgres_dsn("asyncpg"))

    logger.info("API started.")
    yield

    if is_db_initialized() is not None:
        await shutdown_db()

    logger.info("API stopped.")


app = FastAPI(lifespan=lifespan)


# Setup logging as early as possible
configure_logger("api-app")


app.include_router(core_router)
app.include_router(test_router)
app.add_middleware(AccessLogMiddleware)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}

from contextlib import asynccontextmanager
import os
from typing import TypedDict, AsyncIterator, AsyncGenerator

from loguru import logger
from fastapi import FastAPI, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy import text

from src.core.logger import setup_loguru
from src.core.config import get_settings
from src.storage.db import create_async_engine, create_async_sessionmaker

from .routes import core_router
from .middlewares import AccessLogMiddleware


class AppState(TypedDict):
    async_engine: AsyncEngine
    async_sessionmaker: async_sessionmaker[AsyncSession]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting up API...")

    settings = get_settings()
    engine = create_async_engine(
        settings.get_postgres_dsn("asyncpg"),
        echo=settings.DEBUG,
    )
    session_factory = create_async_sessionmaker(engine)

    logger.info("API started.")

    app.state.async_engine = engine
    app.state.async_sessionmaker = session_factory
    yield

    if engine is not None:
        await engine.dispose()

    logger.info("API stopped.")


app = FastAPI(lifespan=lifespan)


# Setup logging as early as possible
setup_loguru(
    service=os.environ.get("APP_SERVICE_NAME", "fastapi-app"),
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


async def get_async_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that provides an AsyncSession per-request.

    Usage:
        async def endpoint(session: AsyncSession = Depends(get_async_session)):
            ...
    """
    session_factory = getattr(request.app.state, "async_sessionmaker", None)
    if session_factory is None:
        # This can happen in tests or if startup didn't run
        logger.warning(
            "Creating session factory on-the-fly, this should not happen in production!",
        )

        settings = get_settings()
        engine = create_async_engine(
            settings.get_postgres_dsn("asyncpg"),
            echo=settings.DEBUG,
        )
        session_factory = create_async_sessionmaker(engine)
        request.app.state.async_engine = engine
        request.app.state.async_sessionmaker = session_factory

    async with session_factory() as session:
        yield session


app.include_router(core_router)
app.add_middleware(AccessLogMiddleware)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}


# Optional: simple DB ping endpoint to validate wiring
@app.get("/db-ping")
async def db_ping(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(text("SELECT 1"))
    val = result.scalar()
    return {"ok": bool(val == 1)}

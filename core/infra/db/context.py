from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from core.config import get_settings
from .connection import create_async_engine, create_async_sessionmaker

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_db(*, dsn: str | None = None, echo: bool | None = None) -> None:
    global _engine, _sessionmaker
    if _engine is not None:
        logger.debug("DB already initialized; skipping re-init")
        return
    settings = get_settings()
    dsn = dsn or settings.get_postgres_dsn("asyncpg")
    echo = settings.DEBUG if echo is None else echo

    _engine = create_async_engine(dsn, echo=echo)
    _sessionmaker = create_async_sessionmaker(_engine)
    logger.info("DB initialized")


def is_db_initialized() -> bool:
    return _engine is not None and _sessionmaker is not None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _sessionmaker is None:
        raise RuntimeError("DB is not initialized. Call init_db() in your entrypoint.")
    return _sessionmaker


def get_sessionmaker_with_init() -> async_sessionmaker[AsyncSession]:
    if not is_db_initialized():
        init_db()
    return get_sessionmaker()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    sm = get_sessionmaker()
    async with sm() as session:
        yield session


async def get_session_with_init() -> AsyncGenerator[AsyncSession, None]:
    if not is_db_initialized():
        init_db()
    async for session in get_session():
        yield session


async def shutdown_db() -> None:
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        logger.info("DB engine disposed")
    _engine = None
    _sessionmaker = None


__all__ = [
    "init_db",
    "is_db_initialized",
    "get_sessionmaker",
    "get_sessionmaker_with_init",
    "get_session",
    "get_session_with_init",
    "shutdown_db",
]

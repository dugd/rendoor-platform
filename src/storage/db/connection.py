from sqlalchemy import create_engine as _create_engine
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine


def create_async_engine(url: str):
    return _create_async_engine(
        url,
    )


def create_sync_engine(url: str):
    return _create_engine(
        url,
    )


def create_async_sessionmaker(engine: AsyncEngine):
    return async_sessionmaker(engine, autoflush=False, expire_on_commit=False)


def create_sync_sessionmaker(engine: Engine):
    return sessionmaker(engine, autoflush=False, expire_on_commit=False)


__all__ = [
    "create_async_engine",
    "create_sync_engine",
    "create_async_sessionmaker",
    "create_sync_sessionmaker",
]

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.db import get_session


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async for s in get_session():
        yield s

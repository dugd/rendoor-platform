from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from core.ports.uow import IUnitOfWork
from core.infra.db.context import get_session
from core.infra.repos import (
    ListingRepository,
    UserRepository,
    FilterRepository,
    SubscriptionRepository,
    OutboxRepository,
)


class SqlAlchemyUoW(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session
        self.listings = ListingRepository(session)
        self.users = UserRepository(session)
        self.filters = FilterRepository(session)
        self.subscriptions = SubscriptionRepository(session)
        self.outbox = OutboxRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self._session.rollback()
        else:
            await self._session.commit()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()


@asynccontextmanager
async def uow_factory():
    async with get_session() as session:
        yield SqlAlchemyUoW(session)

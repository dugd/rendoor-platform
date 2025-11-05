from typing import Protocol
from core.ports.repos import (
    IListingRepository,
    IOutboxRepository,
    IFilterRepository,
    IUserRepository,
    ISubscriptionRepository,
)


class IUnitOfWork(Protocol):
    listings: IListingRepository
    outbox: IOutboxRepository
    filters: IFilterRepository
    users: IUserRepository
    subscriptions: ISubscriptionRepository
    # ...

    async def __aenter__(self) -> "IUnitOfWork": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

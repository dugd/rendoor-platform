from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.notify import Subscription
from core.infra.models.notify import SubscriptionORM
from core.infra.models.user import FilterORM
from core.infra.mappers import SubscriptionMapper


class SubscriptionRepository:
    """SQLAlchemy implementation of subscription repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, subscription: Subscription) -> Subscription:
        """Save or update a subscription"""
        stmt = select(SubscriptionORM).where(SubscriptionORM.id == subscription.id)
        result = await self._session.execute(stmt)
        orm_subscription = result.scalar_one_or_none()

        if orm_subscription:
            # Update existing subscription
            SubscriptionMapper.to_orm(subscription, orm_subscription)
        else:
            # Create new subscription
            orm_subscription = SubscriptionMapper.to_orm(subscription)
            self._session.add(orm_subscription)

        await self._session.flush()
        await self._session.refresh(orm_subscription)

        return SubscriptionMapper.to_domain(orm_subscription)

    async def get_by_id(self, subscription_id: UUID) -> Subscription | None:
        """Get subscription by ID"""
        stmt = select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        result = await self._session.execute(stmt)
        orm_subscription = result.scalar_one_or_none()

        if not orm_subscription:
            return None

        return SubscriptionMapper.to_domain(orm_subscription)

    async def get_by_filter_id(self, filter_id: UUID) -> list[Subscription]:
        """Get all subscriptions for a filter"""
        stmt = select(SubscriptionORM).where(SubscriptionORM.filter_id == filter_id)
        result = await self._session.execute(stmt)
        orm_subscriptions = result.scalars().all()

        return [SubscriptionMapper.to_domain(orm) for orm in orm_subscriptions]

    async def get_all_active(self) -> list[Subscription]:
        """Get all active subscriptions across all users"""
        stmt = select(SubscriptionORM).where(SubscriptionORM.is_active == True)
        result = await self._session.execute(stmt)
        orm_subscriptions = result.scalars().all()

        return [SubscriptionMapper.to_domain(orm) for orm in orm_subscriptions]

    async def get_active_by_user_id(self, user_id: UUID) -> Subscription | None:
        """Get the active subscription for a user (via filter relationship)"""
        stmt = (
            select(SubscriptionORM)
            .join(FilterORM, SubscriptionORM.filter_id == FilterORM.id)
            .where(FilterORM.tg_user_id == user_id)
            .where(SubscriptionORM.is_active == True)
        )
        result = await self._session.execute(stmt)
        orm_subscription = result.scalar_one_or_none()

        if not orm_subscription:
            return None

        return SubscriptionMapper.to_domain(orm_subscription)

    async def get_by_user_id(self, user_id: UUID) -> list[Subscription]:
        """Get all subscriptions for a user (via filter relationship)"""
        stmt = (
            select(SubscriptionORM)
            .join(FilterORM, SubscriptionORM.filter_id == FilterORM.id)
            .where(FilterORM.tg_user_id == user_id)
        )
        result = await self._session.execute(stmt)
        orm_subscriptions = result.scalars().all()

        return [SubscriptionMapper.to_domain(orm) for orm in orm_subscriptions]

    async def deactivate_by_user_id(self, user_id: UUID) -> None:
        """Deactivate all active subscriptions for a user"""
        # Get all filter IDs for this user
        filter_stmt = select(FilterORM.id).where(FilterORM.tg_user_id == user_id)
        filter_result = await self._session.execute(filter_stmt)
        filter_ids = filter_result.scalars().all()

        if not filter_ids:
            return

        # Deactivate subscriptions for these filters
        stmt = (
            update(SubscriptionORM)
            .where(SubscriptionORM.filter_id.in_(filter_ids))
            .where(SubscriptionORM.is_active == True)
            .values(is_active=False)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete(self, subscription_id: UUID) -> None:
        """Delete a subscription"""
        stmt = delete(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        await self._session.execute(stmt)
        await self._session.flush()

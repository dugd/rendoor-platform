from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.user import TgUser
from core.infra.models.user import TgUserORM
from core.infra.mappers import UserMapper
from core.ports.repos.user_repository import UserStats


class UserRepository:
    """SQLAlchemy implementation of user repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: TgUser) -> TgUser:
        """Save or update a user"""
        stmt = select(TgUserORM).where(TgUserORM.tg_user_id == user.tg_user_id)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if orm_user:
            # Update existing user
            UserMapper.to_orm(user, orm_user)
        else:
            # Create new user
            orm_user = UserMapper.to_orm(user)
            self._session.add(orm_user)

        await self._session.flush()
        await self._session.refresh(orm_user)

        return UserMapper.to_domain(orm_user)

    async def get_by_id(self, user_id: UUID) -> TgUser | None:
        """Get user by internal UUID"""
        stmt = select(TgUserORM).where(TgUserORM.id == user_id)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if not orm_user:
            return None

        return UserMapper.to_domain(orm_user)

    async def get_by_tg_user_id(self, tg_user_id: int) -> TgUser | None:
        """Get user by Telegram user ID"""
        stmt = select(TgUserORM).where(TgUserORM.tg_user_id == tg_user_id)
        result = await self._session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if not orm_user:
            return None

        return UserMapper.to_domain(orm_user)

    async def update_last_interaction(
        self, tg_user_id: int, interaction_time: datetime
    ) -> None:
        """Update user's last interaction timestamp"""
        stmt = (
            update(TgUserORM)
            .where(TgUserORM.tg_user_id == tg_user_id)
            .values(last_interaction=interaction_time)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    # ========= Statistics =========

    async def get_user_stats(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> UserStats:
        """Get general user statistics"""
        query = select(
            func.count(TgUserORM.id).label("total_count"),
            func.sum(case((TgUserORM.is_active, 1), else_=0)).label("active_count"),
            func.sum(case((TgUserORM.is_premium, 1), else_=0)).label("premium_count"),
        )

        conditions = []
        if created_after:
            conditions.append(TgUserORM.created_at >= created_after)
        if created_before:
            conditions.append(TgUserORM.created_at <= created_before)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self._session.execute(query)
        row = result.one()

        return UserStats(
            total_count=row.total_count or 0,
            active_count=row.active_count or 0,
            premium_count=row.premium_count or 0,
        )

    async def get_active_users_count(self, since: datetime) -> int:
        """Count users active since a specific time"""
        query = select(func.count(TgUserORM.id)).where(
            TgUserORM.last_interaction >= since
        )

        result = await self._session.execute(query)
        return result.scalar_one()

from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.user import TgUser
from core.infra.models.user import TgUserORM
from core.infra.mappers import UserMapper


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

    async def update_last_interaction(self, tg_user_id: int, interaction_time: datetime) -> None:
        """Update user's last interaction timestamp"""
        stmt = (
            update(TgUserORM)
            .where(TgUserORM.tg_user_id == tg_user_id)
            .values(last_interaction=interaction_time)
        )
        await self._session.execute(stmt)
        await self._session.flush()

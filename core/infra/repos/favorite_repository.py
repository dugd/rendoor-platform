from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.user import Favorite
from core.infra.models.user import FavoriteORM
from core.infra.mappers.favorite_mapper import FavoriteMapper


class FavoriteRepository:
    """SQLAlchemy implementation of favorite repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, favorite: Favorite) -> Favorite:
        """Save a favorite"""
        stmt = select(FavoriteORM).where(FavoriteORM.id == favorite.uuid)
        result = await self._session.execute(stmt)
        orm_favorite = result.scalar_one_or_none()

        if orm_favorite:
            # Update existing favorite (unlikely, but possible)
            FavoriteMapper.to_orm(favorite, orm_favorite)
        else:
            # Create new favorite
            orm_favorite = FavoriteMapper.to_orm(favorite)
            self._session.add(orm_favorite)

        await self._session.flush()
        await self._session.refresh(orm_favorite)

        return FavoriteMapper.to_domain(orm_favorite)

    async def delete(self, favorite_uuid: UUID) -> None:
        """Delete a favorite by UUID"""
        stmt = delete(FavoriteORM).where(FavoriteORM.id == favorite_uuid)
        await self._session.execute(stmt)
        await self._session.flush()

    async def get_by_id(self, favorite_uuid: UUID) -> Favorite | None:
        """Get favorite by UUID"""
        stmt = select(FavoriteORM).where(FavoriteORM.id == favorite_uuid)
        result = await self._session.execute(stmt)
        orm_favorite = result.scalar_one_or_none()

        if not orm_favorite:
            return None

        return FavoriteMapper.to_domain(orm_favorite)

    async def get_by_user_and_listing(
        self, user_id: UUID, listing_id: UUID
    ) -> Favorite | None:
        """Get favorite by user and listing IDs"""
        stmt = select(FavoriteORM).where(
            FavoriteORM.tg_user_id == user_id, FavoriteORM.listing_id == listing_id
        )
        result = await self._session.execute(stmt)
        orm_favorite = result.scalar_one_or_none()

        if not orm_favorite:
            return None

        return FavoriteMapper.to_domain(orm_favorite)

    async def get_user_favorites(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Favorite]:
        """Get all favorites for a user with pagination"""
        stmt = (
            select(FavoriteORM)
            .where(FavoriteORM.tg_user_id == user_id)
            .order_by(FavoriteORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        orm_favorites = result.scalars().all()

        return [FavoriteMapper.to_domain(orm) for orm in orm_favorites]

    # ========= Statistics =========

    async def get_total_count(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of all favorites"""
        query = select(func.count(FavoriteORM.id))

        conditions = []
        if created_after:
            conditions.append(FavoriteORM.created_at >= created_after)
        if created_before:
            conditions.append(FavoriteORM.created_at <= created_before)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self._session.execute(query)
        return result.scalar_one()

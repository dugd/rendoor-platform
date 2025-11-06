from uuid import UUID
from datetime import datetime

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects import postgresql

from core.domain.user import Filter
from core.infra.models.user import FilterORM
from core.infra.models.notify import SubscriptionORM
from core.infra.mappers import FilterMapper
from core.ports.repos.filter_repository import FilterCityStats


class FilterRepository:
    """SQLAlchemy implementation of filter repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, filter_obj: Filter) -> Filter:
        """Save or update a filter"""
        stmt = select(FilterORM).where(FilterORM.id == filter_obj.id)
        result = await self._session.execute(stmt)
        orm_filter = result.scalar_one_or_none()

        if orm_filter:
            # Update existing filter
            FilterMapper.to_orm(filter_obj, orm_filter)
        else:
            # Create new filter
            orm_filter = FilterMapper.to_orm(filter_obj)
            self._session.add(orm_filter)

        await self._session.flush()
        await self._session.refresh(orm_filter)

        return FilterMapper.to_domain(orm_filter)

    async def get_by_id(self, filter_id: UUID) -> Filter | None:
        """Get filter by ID"""
        stmt = select(FilterORM).where(FilterORM.id == filter_id)
        result = await self._session.execute(stmt)
        orm_filter = result.scalar_one_or_none()

        if not orm_filter:
            return None

        return FilterMapper.to_domain(orm_filter)

    async def get_by_user_id(self, user_id: UUID) -> list[Filter]:
        """Get all filters for a user"""
        stmt = select(FilterORM).where(FilterORM.tg_user_id == user_id)
        result = await self._session.execute(stmt)
        orm_filters = result.scalars().all()

        return [FilterMapper.to_domain(orm) for orm in orm_filters]

    async def get_active_filter(self, user_id: UUID) -> Filter | None:
        """Get the active filter for a user by finding the active subscription"""
        stmt = (
            select(FilterORM)
            .join(SubscriptionORM, FilterORM.id == SubscriptionORM.filter_id)
            .where(FilterORM.tg_user_id == user_id)
            .where(SubscriptionORM.is_active)
        )
        result = await self._session.execute(stmt)
        orm_filter = result.scalar_one_or_none()

        if not orm_filter:
            return None

        return FilterMapper.to_domain(orm_filter)

    async def delete(self, filter_id: UUID) -> None:
        """Delete a filter"""
        stmt = delete(FilterORM).where(FilterORM.id == filter_id)
        await self._session.execute(stmt)
        await self._session.flush()

    # ========= Statistics =========

    async def get_popular_cities(
        self,
        limit: int = 10,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[FilterCityStats]:
        """Get most popular cities in filters"""
        city_expr = func.jsonb_extract_path_text(
            FilterORM.criteria.cast(postgresql.JSONB), "location", "city"
        ).label("city")

        count_expr = func.count(FilterORM.id).label("count")

        query = select(city_expr, count_expr).where(city_expr.isnot(None))

        if created_after:
            query = query.where(FilterORM.created_at >= created_after)
        if created_before:
            query = query.where(FilterORM.created_at <= created_before)

        query = query.group_by(city_expr).order_by(count_expr.desc()).limit(limit)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            FilterCityStats(city=row.city, count=row.count) for row in rows if row.city
        ]

    async def get_total_count(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of filters"""
        query = select(func.count(FilterORM.id))

        conditions = []
        if created_after:
            conditions.append(FilterORM.created_at >= created_after)
        if created_before:
            conditions.append(FilterORM.created_at <= created_before)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self._session.execute(query)
        return result.scalar_one()

from typing import Any
from datetime import datetime
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.domain.listing import Listing
from core.infra.models import ListingORM, ListingPhotoORM
from core.infra.mappers import ListingMapper
from core.ports.repos.listing_repository import ListingStatsByCity


class ListingRepository:
    """SQLAlchemy implementation of listing repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    # ========= CRUD =========

    async def save(self, listing: Listing) -> Listing:
        """
        Upsert за доменним UUID (Listing.uuid).
        Фото синхронізуються дифом.
        """
        stmt = (
            select(ListingORM)
            .options(selectinload(ListingORM.photos))
            .where(ListingORM.id == listing.uuid)
        )
        orm_listing = (await self._session.execute(stmt)).scalar_one_or_none()

        if orm_listing is None:
            # create
            orm_listing = ListingMapper.to_orm(listing, orm=None)
            self._session.add(orm_listing)
        else:
            # update in-place
            ListingMapper.to_orm(listing, orm=orm_listing)

        await self._session.flush()

        # sync photos
        await self._sync_photos(orm_listing.id, listing)

        await self._session.flush()
        await self._session.refresh(orm_listing)

        return ListingMapper.to_domain(orm_listing)

    async def get_by_id(self, listing_id: Any) -> Listing | None:
        """
        Повертає домен за PK/UUID. Тип Any, бо у тебе PK = UUID.
        """
        stmt = (
            select(ListingORM)
            .options(
                selectinload(ListingORM.photos),
            )
            .where(ListingORM.id == listing_id)
        )
        orm_listing = (await self._session.execute(stmt)).scalar_one_or_none()
        return ListingMapper.to_domain(orm_listing) if orm_listing else None

    async def find_by_fingerprint(self, fingerprint: str) -> list[Listing]:
        stmt = (
            select(ListingORM)
            .options(selectinload(ListingORM.photos))
            .where(ListingORM.fingerprint == fingerprint)
        )
        orm_listings = (await self._session.execute(stmt)).scalars().all()
        return [ListingMapper.to_domain(orm) for orm in orm_listings]

    async def find_by_source_and_external_id(
        self, source_code: str, external_id: str
    ) -> Listing | None:
        """
        Без join: тримаємо денормалізоване поле source_code у ListingORM.
        Якщо в тебе зв’язок через SourceORM — додай .join і .where по SourceORM.code.
        """
        stmt = (
            select(ListingORM)
            .options(selectinload(ListingORM.photos))
            .where(
                ListingORM.source_code == source_code,
                ListingORM.external_id == external_id,
            )
        )
        orm_listing = (await self._session.execute(stmt)).scalar_one_or_none()
        return ListingMapper.to_domain(orm_listing) if orm_listing else None

    # ========= internal =========

    async def _sync_photos(self, listing_id: Any, listing: Listing) -> None:
        """
        Диф-синхронізація фото:
        - видаляємо відсутні,
        - оновлюємо існуючі,
        - додаємо нові.
        Очікується, що order є стабільним ключем у межах listing.
        """
        # поточні з БД
        stmt = select(ListingPhotoORM).where(ListingPhotoORM.listing_id == listing_id)
        current = (await self._session.execute(stmt)).scalars().all()
        by_order = {p.order: p for p in current}

        # таргет зі строк
        target_by_order = {img.order: img for img in (listing.photos or [])}

        # видалення
        to_delete_orders = set(by_order) - set(target_by_order)
        if to_delete_orders:
            await self._session.execute(
                delete(ListingPhotoORM).where(
                    ListingPhotoORM.listing_id == listing_id,
                    ListingPhotoORM.order.in_(to_delete_orders),
                )
            )

        # апдейти + вставки
        for order, img in target_by_order.items():
            if order in by_order:
                ph = by_order[order]
                if ph.url != img.url:
                    ph.url = img.url
            else:
                self._session.add(
                    ListingPhotoORM(**ListingMapper.photo_to_orm_dict(listing_id, img))
                )

    # ========= Statistics =========

    async def get_stats_by_city(
        self,
        only_active: bool = True,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[ListingStatsByCity]:
        """Get statistics grouped by city"""
        query = select(
            ListingORM.address_city.label("city"),
            func.count(ListingORM.id).label("count"),
            func.avg(ListingORM.price_amount).label("avg_price"),
            func.min(ListingORM.price_amount).label("min_price"),
            func.max(ListingORM.price_amount).label("max_price"),
        ).where(ListingORM.address_city.isnot(None))

        conditions = []
        if only_active:
            conditions.append(not ListingORM.is_archived)
        if created_after:
            conditions.append(ListingORM.created_at >= created_after)
        if created_before:
            conditions.append(ListingORM.created_at <= created_before)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.group_by(ListingORM.address_city).order_by(
            func.count(ListingORM.id).desc()
        )

        result = await self._session.execute(query)
        rows = result.all()

        return [
            ListingStatsByCity(
                city=row.city,
                count=row.count,
                avg_price=float(row.avg_price) if row.avg_price else None,
                min_price=float(row.min_price) if row.min_price else None,
                max_price=float(row.max_price) if row.max_price else None,
            )
            for row in rows
        ]

    async def get_total_count(
        self,
        city: str | None = None,
        only_active: bool = True,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of listings with optional filters"""
        query = select(func.count(ListingORM.id))

        conditions = []
        if only_active:
            conditions.append(not ListingORM.is_archived)
        if city:
            conditions.append(ListingORM.address_city == city)
        if created_after:
            conditions.append(ListingORM.created_at >= created_after)
        if created_before:
            conditions.append(ListingORM.created_at <= created_before)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self._session.execute(query)
        return result.scalar_one()

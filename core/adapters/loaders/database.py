"""Database loader for persisting listings to PostgreSQL."""

from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.domain.listing import Listing
from core.domain.ingest import RawListing
from core.infra.mappers import RawListingMapper, ListingMapper
from core.infra.models import (
    SourceORM,
    RawListingORM,
    ListingORM,
    ListingPhotoORM,
)


class DatabaseListingLoader:
    """
    Database-backed loader for persisting listings to PostgreSQL.

    Uses mappers to convert between domain entities and ORM models,
    following the repository pattern.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the database loader.

        Args:
            session: SQLAlchemy async session for database operations
        """
        self._session = session

    async def save_raw(self, raw: RawListing) -> RawListing:
        """
        Save a raw listing to the database.

        Uses INSERT ... ON CONFLICT to handle duplicates based on
        (source_code, external_id) unique constraint.

        Args:
            raw: RawListing to save

        Returns:
            RawListing with updated UUID
        """
        # Get or create source
        await self._get_or_create_source(raw.source_code)

        raw_dict = RawListingMapper.to_orm_dict(raw)

        # Build insert statement with ON CONFLICT
        stmt = pg_insert(RawListingORM).values(**raw_dict)

        # On conflict, update the payload and fetch info
        stmt = stmt.on_conflict_do_update(
            constraint="uq_raw_src_ext",
            set_={
                "payload": stmt.excluded.payload,
                "schema_version": stmt.excluded.schema_version,
                "fetch_url": stmt.excluded.fetch_url,
                "fetched_at": stmt.excluded.fetched_at,
                "processing_status": stmt.excluded.processing_status,
                "processing_error": stmt.excluded.processing_error,
                "processed_at": stmt.excluded.processed_at,
            },
        )

        await self._session.execute(stmt)
        await self._session.commit()

        return raw

    async def save_listing(self, listing: Listing) -> Listing:
        """
        Save a normalized listing to the database.

        Handles:
        - Upserting the listing
        - Saving photos

        Args:
            listing: Listing to save

        Returns:
            Listing with updated timestamps
        """
        # Get or create source
        await self._get_or_create_source(listing.source_code)

        # Use mapper to convert to ORM dict
        listing_values = ListingMapper.to_orm_dict(listing)

        # Build listing insert with ON CONFLICT
        stmt = pg_insert(ListingORM).values(**listing_values)

        # On conflict, update mutable fields
        stmt = stmt.on_conflict_do_update(
            constraint="uq_listing_src_ext",
            set_={
                "last_seen_at": stmt.excluded.last_seen_at,
                "price_amount": stmt.excluded.price_amount,
                "price_currency": stmt.excluded.price_currency,
                "status": stmt.excluded.status,
                "description": stmt.excluded.description,
                "external_owner_id": stmt.excluded.external_owner_id,
                "owner_name": stmt.excluded.owner_name,
                "owner_type_declared": stmt.excluded.owner_type_declared,
                "owner_contacts": stmt.excluded.owner_contacts,
                "is_archived": stmt.excluded.is_archived,
                "listing_updated_at": stmt.excluded.listing_updated_at,
            },
        ).returning(
            ListingORM.id,
            ListingORM.created_at,
            ListingORM.updated_at,
            ListingORM.listing_created_at,
            ListingORM.listing_updated_at,
        )

        result = await self._session.execute(stmt)
        row = result.one()

        # Update listing with DB-generated values
        listing.uuid = row.id
        listing.created_at = row.listing_created_at or row.created_at
        listing.updated_at = row.listing_updated_at or row.updated_at

        # Save photos if present
        if listing.photos:
            await self._save_photos(listing.uuid, listing.photos)

        await self._session.commit()

        return listing

    async def bulk_save_raw(self, raws: list[RawListing]) -> list[RawListing]:
        """
        Save multiple raw listings in bulk for better performance.

        Args:
            raws: List of RawListings to save

        Returns:
            List of RawListings (unchanged)
        """
        if not raws:
            return []

        # Get or create source (assuming all from same source)
        source_code = raws[0].source_code
        await self._get_or_create_source(source_code)

        # Prepare bulk insert values using mapper
        values = [RawListingMapper.to_orm_dict(raw) for raw in raws]

        # Build bulk insert with ON CONFLICT
        stmt = pg_insert(RawListingORM).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_raw_src_ext",
            set_={
                "payload": stmt.excluded.payload,
                "schema_version": stmt.excluded.schema_version,
                "fetch_url": stmt.excluded.fetch_url,
                "fetched_at": stmt.excluded.fetched_at,
                "processing_status": stmt.excluded.processing_status,
                "processing_error": stmt.excluded.processing_error,
                "processed_at": stmt.excluded.processed_at,
            },
        )

        await self._session.execute(stmt)
        await self._session.commit()

        return raws

    async def bulk_save_listings(self, listings: list[Listing]) -> list[Listing]:
        """
        Save multiple normalized listings in bulk for better performance.

        Args:
            listings: List of Listings to save

        Returns:
            List of Listings with updated timestamps
        """
        if not listings:
            return []

        # Get or create source (assuming all from same source)
        source_code = listings[0].source_code
        await self._get_or_create_source(source_code)

        # Prepare bulk insert values using mapper
        values = [ListingMapper.to_orm_dict(listing) for listing in listings]

        attempted_map = {
            (v.get("source_code"), v.get("external_id")): v.get("id") for v in values
        }

        # Build bulk insert with ON CONFLICT
        stmt = pg_insert(ListingORM).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_listing_src_ext",
            set_={
                "last_seen_at": stmt.excluded.last_seen_at,
                "price_amount": stmt.excluded.price_amount,
                "price_currency": stmt.excluded.price_currency,
                "status": stmt.excluded.status,
                "description": stmt.excluded.description,
                "external_owner_id": stmt.excluded.external_owner_id,
                "owner_name": stmt.excluded.owner_name,
                "owner_type_declared": stmt.excluded.owner_type_declared,
                "owner_contacts": stmt.excluded.owner_contacts,
                "is_archived": stmt.excluded.is_archived,
                "listing_updated_at": stmt.excluded.listing_updated_at,
            },
        ).returning(
            ListingORM.id,
            ListingORM.source_code,
            ListingORM.external_id,
            ListingORM.created_at,
            ListingORM.updated_at,
            ListingORM.listing_created_at,
            ListingORM.listing_updated_at,
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        # Map new values back to Listings
        new_values_map = {
            (row.source_code, row.external_id): {
                "id": row.id,
                "attempted_id": attempted_map.get((row.source_code, row.external_id)),
                "created_at": row.listing_created_at or row.created_at,
                "updated_at": row.listing_updated_at or row.updated_at,
            }
            for row in rows
        }

        # Update listings with DB values
        for listing in listings:
            natural_key = listing.natural_key  # (source_code, external_id)
            if natural_key in new_values_map:
                data = new_values_map[natural_key]
                listing.uuid = data["id"]
                listing.created_at = data["created_at"]
                listing.updated_at = data["updated_at"]

        # Save photos for each listing in bulk
        await self._bulk_save_all_photos(listings)

        await self._session.commit()

        return listings

    async def get_listing_by_natural_key(
        self, source_code: str, external_id: str
    ) -> Listing | None:
        """
        Get a listing by its natural key (source_code, external_id).

        Args:
            source_code: Source code
            external_id: External ID from source

        Returns:
            Listing if found, None otherwise
        """
        stmt = select(ListingORM).where(
            ListingORM.source_code == source_code,
            ListingORM.external_id == external_id,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return ListingMapper.to_domain(orm)

    async def get_listing_by_uuid(self, uuid: UUID) -> Listing | None:
        """
        Get a listing by UUID.

        Args:
            uuid: Listing UUID

        Returns:
            Listing if found, None otherwise
        """
        stmt = select(ListingORM).where(ListingORM.id == uuid)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()

        if orm is None:
            return None

        return ListingMapper.to_domain(orm)

    async def _get_or_create_source(self, source_code: str) -> SourceORM:
        """
        Get or create a source by code.

        Args:
            source_code: Source code to get or create

        Returns:
            SourceORM instance
        """
        stmt = select(SourceORM).where(SourceORM.code == source_code)
        result = await self._session.execute(stmt)
        source = result.scalar_one_or_none()

        if source is None:
            # Create new source with default values
            source = SourceORM(
                code=source_code,
                name=source_code.upper(),
                type="website",
                is_active=True,
            )
            self._session.add(source)
            await self._session.flush()

        return source

    async def _save_photos(self, listing_uuid: UUID, photos: list[Any]) -> None:
        """
        Save photos for a listing, replacing old ones.

        Args:
            listing_uuid: UUID of the listing
            photos: List of Image value objects
        """
        # Delete existing photos
        stmt = delete(ListingPhotoORM).where(ListingPhotoORM.listing_id == listing_uuid)
        await self._session.execute(stmt)

        # Insert new photos using mapper
        if photos:
            photo_values = [
                ListingMapper.photo_to_orm_dict(listing_uuid, photo) for photo in photos
            ]
            stmt = insert(ListingPhotoORM).values(photo_values)
            await self._session.execute(stmt)

    async def _bulk_save_all_photos(self, listings: list[Listing]) -> None:
        """
        Save photos for multiple listings in bulk.

        Args:
            listings: List of Listing entities with photos
        """
        # Collect all listing UUIDs that have photos
        listing_uuids_with_photos = [
            listing.uuid for listing in listings if listing.photos
        ]

        if not listing_uuids_with_photos:
            return

        # Delete existing photos for all listings in one query
        stmt = delete(ListingPhotoORM).where(
            ListingPhotoORM.listing_id.in_(listing_uuids_with_photos)
        )
        await self._session.execute(stmt)

        # Prepare all photo values for bulk insert
        all_photo_values = []
        for listing in listings:
            if listing.photos:
                photo_values = [
                    ListingMapper.photo_to_orm_dict(listing.uuid, photo)
                    for photo in listing.photos
                ]
                all_photo_values.extend(photo_values)

        # Insert all photos in one query
        if all_photo_values:
            stmt = insert(ListingPhotoORM).values(all_photo_values)
            await self._session.execute(stmt)


__all__ = ["DatabaseListingLoader"]

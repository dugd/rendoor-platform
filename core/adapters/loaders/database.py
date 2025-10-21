"""
Database implementation of ListingLoader.

This module provides a concrete implementation of the ListingLoader protocol
that saves listings to a PostgreSQL database using SQLAlchemy ORM.
"""

import hashlib
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from core.domain.listing import Listing
from core.domain.ingest import RawListing
from core.infra.models import (
    SourceORM,
    RawListingORM,
    ListingORM,
    ListingPhotoORM,
    OwnerORM,
)


class DatabaseListingLoader:
    """
    Database-backed loader for persisting listings to PostgreSQL.

    Implements the ListingLoader protocol using SQLAlchemy ORM.
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
        (source_id, external_id) unique constraint.

        Args:
            raw: RawListing to save

        Returns:
            RawListing with updated ID
        """
        # Get or create source
        source = await self._get_or_create_source(raw.source_code)

        # Build insert statement with ON CONFLICT
        stmt = pg_insert(RawListingORM).values(
            source_id=source.id,
            external_id=raw.external_id,
            payload=raw.payload,
            schema_version=raw.schema_version,
            fetch_url=raw.fetch_url,
            fetched_at=raw.fetched_at,
            processing_status=raw.processing_status,
            processing_error=raw.processing_error,
            processed_at=raw.processed_at,
        )

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
        ).returning(RawListingORM.id)

        result = await self._session.execute(stmt)
        raw_id = result.scalar_one()

        # Return updated RawListing with ID
        return RawListing(
            raw_id=raw_id,
            source_code=raw.source_code,
            external_id=raw.external_id,
            payload=raw.payload,
            schema_version=raw.schema_version,
            fetch_url=raw.fetch_url,
            fetched_at=raw.fetched_at,
            processing_status=raw.processing_status,
            processing_error=raw.processing_error,
            processed_at=raw.processed_at,
        )

    async def save_listing(self, listing: Listing) -> Listing:
        """
        Save a normalized listing to the database.

        Handles:
        - Creating/updating owner if owner_info is present
        - Upserting the listing
        - Saving photos

        Args:
            listing: Listing to save

        Returns:
            Listing with updated ID and timestamps
        """
        # Get or create source
        source = await self._get_or_create_source(listing.source_code)

        # Handle owner if present
        owner_id = listing.owner_id
        if listing.owner_info and not owner_id:
            owner_id = await self._get_or_create_owner(listing.owner_info)

        # Prepare location for PostGIS
        location_wkb = None
        if listing.location:
            point = Point(listing.location.longitude, listing.location.latitude)
            location_wkb = from_shape(point, srid=4326)

        # Build listing insert with ON CONFLICT
        listing_values = {
            "source_id": source.id,
            "external_id": listing.external_id,
            "owner_id": owner_id,
            "url": listing.url,
            "title": listing.title,
            "fingerprint": listing.fingerprint,
            "price_amount": listing.price.amount if listing.price else None,
            "price_currency": listing.price.currency if listing.price else None,
            "address_country": listing.address.country if listing.address else None,
            "address_state": listing.address.state if listing.address else None,
            "address_city": listing.address.city if listing.address else None,
            "address_district": listing.address.district if listing.address else None,
            "address_street": listing.address.street if listing.address else None,
            "address_building": listing.address.building if listing.address else None,
            "address_zip": listing.address.zip_code if listing.address else None,
            "location": location_wkb,
            "room_count": listing.room_count,
            "area": listing.area,
            "floor": listing.floor,
            "total_floors": listing.total_floors,
            "description": listing.description,
            "owner_name": listing.owner_info.name if listing.owner_info else None,
            "owner_type_declared": listing.owner_info.owner_type if listing.owner_info else None,
            "status": listing.status,
            "is_verified": listing.is_verified,
            "view_count": listing.view_count,
            "first_seen_at": listing.first_seen_at,
            "last_seen_at": listing.last_seen_at,
        }

        stmt = pg_insert(ListingORM).values(**listing_values)

        # On conflict, update last_seen_at and other mutable fields
        stmt = stmt.on_conflict_do_update(
            constraint="uq_listing_src_ext",
            set_={
                "last_seen_at": stmt.excluded.last_seen_at,
                "price_amount": stmt.excluded.price_amount,
                "price_currency": stmt.excluded.price_currency,
                "status": stmt.excluded.status,
                "view_count": stmt.excluded.view_count,
                "description": stmt.excluded.description,
                "owner_id": stmt.excluded.owner_id,
            },
        ).returning(ListingORM.id, ListingORM.created_at, ListingORM.updated_at)

        result = await self._session.execute(stmt)
        row = result.one()
        listing_id = row.id
        created_at = row.created_at
        updated_at = row.updated_at

        # Save photos if present
        if listing.photos:
            await self._save_photos(listing_id, listing.photos)

        # Update listing with DB-generated values
        listing.id = listing_id
        listing.created_at = created_at
        listing.updated_at = updated_at
        if owner_id:
            listing.owner_id = owner_id

        await self._session.commit()

        return listing

    async def bulk_save_raw(self, raws: list[RawListing]) -> list[RawListing]:
        """
        Save multiple raw listings in bulk for better performance.

        Args:
            raws: List of RawListings to save

        Returns:
            List of RawListings with updated IDs
        """
        if not raws:
            return []

        # Get or create source (assuming all from same source)
        source_code = raws[0].source_code
        source = await self._get_or_create_source(source_code)

        # Prepare bulk insert values
        values = [
            {
                "source_id": source.id,
                "external_id": raw.external_id,
                "payload": raw.payload,
                "schema_version": raw.schema_version,
                "fetch_url": raw.fetch_url,
                "fetched_at": raw.fetched_at,
                "processing_status": raw.processing_status,
                "processing_error": raw.processing_error,
                "processed_at": raw.processed_at,
            }
            for raw in raws
        ]

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
        ).returning(RawListingORM.id, RawListingORM.external_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        await self._session.commit()

        # Map IDs back to RawListings
        id_map = {row.external_id: row.id for row in rows}

        return [
            RawListing(
                raw_id=id_map.get(raw.external_id),
                source_code=raw.source_code,
                external_id=raw.external_id,
                payload=raw.payload,
                schema_version=raw.schema_version,
                fetch_url=raw.fetch_url,
                fetched_at=raw.fetched_at,
                processing_status=raw.processing_status,
                processing_error=raw.processing_error,
                processed_at=raw.processed_at,
            )
            for raw in raws
        ]

    async def bulk_save_listings(self, listings: list[Listing]) -> list[Listing]:
        """
        Save multiple normalized listings in bulk for better performance.

        Args:
            listings: List of Listings to save

        Returns:
            List of Listings with updated IDs and timestamps
        """
        if not listings:
            return []

        # Get or create source (assuming all from same source)
        source_code = listings[0].source_code
        source = await self._get_or_create_source(source_code)

        # Process owners in bulk
        for listing in listings:
            if listing.owner_info and not listing.owner_id:
                owner_id = await self._get_or_create_owner(listing.owner_info)
                listing.owner_id = owner_id

        # Prepare bulk insert values
        values = []
        for listing in listings:
            location_wkb = None
            if listing.location:
                point = Point(listing.location.longitude, listing.location.latitude)
                location_wkb = from_shape(point, srid=4326)

            values.append({
                "source_id": source.id,
                "external_id": listing.external_id,
                "owner_id": listing.owner_id,
                "url": listing.url,
                "title": listing.title,
                "fingerprint": listing.fingerprint,
                "price_amount": listing.price.amount if listing.price else None,
                "price_currency": listing.price.currency if listing.price else None,
                "address_country": listing.address.country if listing.address else None,
                "address_state": listing.address.state if listing.address else None,
                "address_city": listing.address.city if listing.address else None,
                "address_district": listing.address.district if listing.address else None,
                "address_street": listing.address.street if listing.address else None,
                "address_building": listing.address.building if listing.address else None,
                "address_zip": listing.address.zip_code if listing.address else None,
                "location": location_wkb,
                "room_count": listing.room_count,
                "area": listing.area,
                "floor": listing.floor,
                "total_floors": listing.total_floors,
                "description": listing.description,
                "owner_name": listing.owner_info.name if listing.owner_info else None,
                "owner_type_declared": listing.owner_info.owner_type if listing.owner_info else None,
                "status": listing.status,
                "is_verified": listing.is_verified,
                "view_count": listing.view_count,
                "first_seen_at": listing.first_seen_at,
                "last_seen_at": listing.last_seen_at,
            })

        # Build bulk insert with ON CONFLICT
        stmt = pg_insert(ListingORM).values(values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_listing_src_ext",
            set_={
                "last_seen_at": stmt.excluded.last_seen_at,
                "price_amount": stmt.excluded.price_amount,
                "price_currency": stmt.excluded.price_currency,
                "status": stmt.excluded.status,
                "view_count": stmt.excluded.view_count,
                "description": stmt.excluded.description,
                "owner_id": stmt.excluded.owner_id,
            },
        ).returning(ListingORM.id, ListingORM.external_id, ListingORM.created_at, ListingORM.updated_at)

        result = await self._session.execute(stmt)
        rows = result.all()

        # Map IDs back to Listings
        id_map = {row.external_id: {"id": row.id, "created_at": row.created_at, "updated_at": row.updated_at} for row in rows}

        # Update listings with DB values
        for listing in listings:
            if listing.external_id in id_map:
                data = id_map[listing.external_id]
                listing.id = data["id"]
                listing.created_at = data["created_at"]
                listing.updated_at = data["updated_at"]

        # Save photos for each listing
        for listing in listings:
            if listing.photos and listing.id:
                await self._save_photos(listing.id, listing.photos)

        await self._session.commit()

        return listings

    async def _get_or_create_source(self, source_code: str) -> SourceORM:
        """Get or create a source by code."""
        stmt = select(SourceORM).where(SourceORM.code == source_code)
        result = await self._session.execute(stmt)
        source = result.scalar_one_or_none()

        if source is None:
            # Create new source
            source = SourceORM(
                code=source_code,
                name=source_code.upper(),
                is_active=True,
            )
            self._session.add(source)
            await self._session.flush()

        return source

    async def _get_or_create_owner(self, owner_info: Any) -> int:
        """
        Get or create owner from OwnerInfo.

        Uses fingerprint based on contact info to detect duplicates.
        """
        # Generate fingerprint from contact info
        fingerprint = self._generate_owner_fingerprint(owner_info)

        # Try to find existing owner
        stmt = select(OwnerORM).where(OwnerORM.fingerprint == fingerprint)
        result = await self._session.execute(stmt)
        owner = result.scalar_one_or_none()

        if owner is None:
            # Create new owner
            contact = owner_info.contact
            owner = OwnerORM(
                fingerprint=fingerprint,
                name=owner_info.name,
                owner_type=owner_info.owner_type,
                contact_phone=contact.phone if contact else None,
                contact_telegram=contact.telegram if contact else None,
                contact_viber=contact.viber if contact else None,
                contact_whatsapp=contact.whatsapp if contact else None,
                contact_email=contact.email if contact else None,
                rating=0.0,
                listing_count=0,
                verified=False,
            )
            self._session.add(owner)
            await self._session.flush()

        return owner.id

    def _generate_owner_fingerprint(self, owner_info: Any) -> str:
        """Generate unique fingerprint for owner based on contact info."""
        parts = []

        if owner_info.contact:
            if owner_info.contact.phone:
                # Normalize phone number
                phone = "".join(c for c in owner_info.contact.phone if c.isdigit())
                parts.append(f"phone:{phone}")
            if owner_info.contact.email:
                parts.append(f"email:{owner_info.contact.email.lower()}")
            if owner_info.contact.telegram:
                parts.append(f"tg:{owner_info.contact.telegram.lower()}")

        if not parts and owner_info.name:
            # Fallback to name if no contact info
            parts.append(f"name:{owner_info.name.lower()}")

        if not parts:
            # Last resort: random fingerprint
            parts.append("unknown")

        key = "|".join(parts)
        return hashlib.sha256(key.encode()).hexdigest()[:64]

    async def _save_photos(self, listing_id: int, photos: list[Any]) -> None:
        """Save photos for a listing, replacing old ones."""
        # Delete existing photos
        from sqlalchemy import delete
        stmt = delete(ListingPhotoORM).where(ListingPhotoORM.listing_id == listing_id)
        await self._session.execute(stmt)

        # Insert new photos
        if photos:
            photo_values = [
                {
                    "listing_id": listing_id,
                    "url": photo.url,
                    "order": photo.order,
                }
                for photo in photos
            ]
            stmt = insert(ListingPhotoORM).values(photo_values)
            await self._session.execute(stmt)


__all__ = ["DatabaseListingLoader"]

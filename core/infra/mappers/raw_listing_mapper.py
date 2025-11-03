"""Mapper for RawListing domain entity and RawListingORM."""

from core.domain.ingest import RawListing
from core.infra.models.ingest import RawListingORM


class RawListingMapper:
    """Mapper for converting between RawListing domain entity and RawListingORM."""

    @staticmethod
    def to_domain(orm: RawListingORM) -> RawListing:
        """
        Convert RawListingORM to RawListing domain entity.

        Args:
            orm: ORM model instance

        Returns:
            RawListing domain entity
        """
        return RawListing(
            uuid=orm.id,
            source_code=orm.source_code,
            external_id=orm.external_id,
            payload=orm.payload,
            schema_version=orm.schema_version,
            fetch_url=orm.fetch_url,
            fetched_at=orm.fetched_at,
            processing_status=orm.processing_status,
            processing_error=orm.processing_error,
            processed_at=orm.processed_at,
        )

    @staticmethod
    def to_orm_dict(raw: RawListing) -> dict:
        """
        Convert RawListing domain entity to dictionary for ORM insertion.

        Args:
            raw: Domain entity

        Returns:
            Dictionary with ORM-compatible field names and values
        """
        return {
            "id": raw.uuid,
            "source_code": raw.source_code,
            "external_id": raw.external_id,
            "payload": raw.payload,
            "schema_version": raw.schema_version,
            "fetch_url": raw.fetch_url,
            "fetched_at": raw.fetched_at,
            "processing_status": raw.processing_status,
            "processing_error": raw.processing_error,
            "processed_at": raw.processed_at,
        }

    @staticmethod
    def to_orm(raw: RawListing, orm: RawListingORM | None = None) -> RawListingORM:
        """
        Convert RawListing domain entity to RawListingORM.

        Args:
            raw: Domain entity
            orm: Existing ORM object to update (optional)

        Returns:
            RawListingORM instance
        """
        if orm is None:
            orm = RawListingORM(
                id=raw.uuid,
                source_code=raw.source_code,
                external_id=raw.external_id,
            )

        # Update all fields
        orm.payload = raw.payload
        orm.schema_version = raw.schema_version
        orm.fetch_url = raw.fetch_url
        orm.fetched_at = raw.fetched_at
        orm.processing_status = raw.processing_status
        orm.processing_error = raw.processing_error
        orm.processed_at = raw.processed_at

        return orm


__all__ = ["RawListingMapper"]

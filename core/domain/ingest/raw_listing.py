from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime, timezone

from .value import RawStatus


@dataclass(frozen=True)
class RawListing:
    """
    Raw listing from source before processing.

    Immutable entity that stores original data in the form
    in which it came from the source.
    """

    source_code: str
    external_id: str
    payload: dict[str, Any]
    schema_version: str
    fetch_url: str | None
    fetched_at: datetime
    processing_error: str | None = None
    processed_at: datetime | None = None
    processing_status: RawStatus = "processing"
    uuid: UUID = field(default_factory=uuid4)

    @property
    def natural_key(self) -> tuple[str, str]:
        """Unique key within the source"""
        return self.source_code, self.external_id

    def mark_processing(self) -> "RawListing":
        """Marks as being processed"""
        return self._copy_with(processing_status="processing")

    def mark_processed(self) -> "RawListing":
        """Marks as processed"""
        return self._copy_with(
            processing_status="processed",
            processed_at=datetime.now(timezone.utc),
        )

    def mark_failed(self, error: str) -> "RawListing":
        """Marks as failed"""
        return self._copy_with(
            processing_status="failed",
            processing_error=error,
            processed_at=datetime.now(timezone.utc),
        )

    def mark_skipped(self, reason: str) -> "RawListing":
        """Marks as skipped"""
        return self._copy_with(
            processing_status="skipped",
            processing_error=reason,
            processed_at=datetime.now(timezone.utc),
        )

    def _copy_with(
        self,
        *,
        payload: dict[str, Any] | None = None,
        schema_version: str | None = None,
        fetch_url: str | None | type(...) = ...,
        fetched_at: datetime | None = None,
        processing_status: RawStatus | None = None,
        processing_error: str | None | type(...) = ...,
        processed_at: datetime | None | type(...) = ...,
    ) -> "RawListing":
        """Creates a copy with updated fields"""
        return RawListing(
            uuid=self.uuid,
            source_code=self.source_code,
            external_id=self.external_id,
            payload=payload if payload is not None else dict(self.payload),
            schema_version=schema_version or self.schema_version,
            fetch_url=self.fetch_url if fetch_url is ... else fetch_url,
            fetched_at=fetched_at or self.fetched_at,
            processing_status=processing_status or self.processing_status,
            processing_error=self.processing_error
            if processing_error is ...
            else processing_error,
            processed_at=self.processed_at if processed_at is ... else processed_at,
        )

    def __repr__(self) -> str:
        return (
            f"RawListing(uuid={self.uuid}, source='{self.source_code}', "
            f"external_id='{self.external_id}', status='{self.processing_status}')"
        )

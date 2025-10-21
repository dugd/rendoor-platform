from typing import Any
from datetime import datetime, timezone


class RawListing:
    """
    Raw listing from source before processing.

    Immutable entity that stores original data in the form
    in which it came from the source.
    """

    __slots__ = (
        "_id",
        "_source_code",
        "_external_id",
        "_payload",
        "_schema_version",
        "_fetch_url",
        "_fetched_at",
        "_processing_status",
        "_processing_error",
        "_processed_at",
        "_frozen",
    )

    def __init__(
        self,
        source_code: str,
        external_id: str,
        payload: dict[str, Any],
        *,
        raw_id: int | None = None,
        schema_version: str = "1.0",
        fetch_url: str | None = None,
        fetched_at: datetime | None = None,
        processing_status: str = "pending",
        processing_error: str | None = None,
        processed_at: datetime | None = None,
    ):
        if not source_code or not isinstance(source_code, str):
            raise ValueError("source_code must be non-empty str")
        if not external_id or not isinstance(external_id, str):
            raise ValueError("external_id must be non-empty str")
        if not isinstance(payload, dict):
            raise TypeError("payload must be dict")

        self._id = raw_id
        self._source_code = source_code.strip().lower()
        self._external_id = external_id.strip()
        self._payload = dict(payload)
        self._schema_version = schema_version.strip()
        self._fetch_url = fetch_url
        self._fetched_at = fetched_at or datetime.now(timezone.utc)
        self._processing_status = processing_status
        self._processing_error = processing_error
        self._processed_at = processed_at
        self._frozen = True

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def source_code(self) -> str:
        return self._source_code

    @property
    def external_id(self) -> str:
        return self._external_id

    @property
    def payload(self) -> dict[str, Any]:
        return self._payload

    @property
    def schema_version(self) -> str:
        return self._schema_version

    @property
    def fetch_url(self) -> str | None:
        return self._fetch_url

    @property
    def fetched_at(self) -> datetime:
        return self._fetched_at

    @property
    def processing_status(self) -> str:
        return self._processing_status

    @property
    def processing_error(self) -> str | None:
        return self._processing_error

    @property
    def processed_at(self) -> datetime | None:
        return self._processed_at

    @property
    def natural_key(self) -> tuple[str, str]:
        """Unique key within the source"""
        return self._source_code, self._external_id

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
        processing_status: str | None = None,
        processing_error: str | None | type(...) = ...,
        processed_at: datetime | None | type(...) = ...,
    ) -> "RawListing":
        """Creates a copy with updated fields"""
        return RawListing(
            raw_id=self._id,
            source_code=self._source_code,
            external_id=self._external_id,
            payload=payload if payload is not None else dict(self._payload),
            schema_version=schema_version or self._schema_version,
            fetch_url=self._fetch_url if fetch_url is ... else fetch_url,
            fetched_at=fetched_at or self._fetched_at,
            processing_status=processing_status or self._processing_status,
            processing_error=self._processing_error
            if processing_error is ...
            else processing_error,
            processed_at=self._processed_at if processed_at is ... else processed_at,
        )

    def __setattr__(self, key, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen RawListing: {key}={value}")
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        return (
            f"RawListing(id={self._id}, source='{self._source_code}', "
            f"external_id='{self._external_id}', status='{self._processing_status}')"
        )

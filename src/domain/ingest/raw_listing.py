from typing import Any
from datetime import datetime, timezone


class RawListing:
    __slots__ = (
        "_source_id",
        "_external_id",
        "_payload",
        "_url",
        "_fetched_at",
        "_frozen",
    )

    def __init__(
        self,
        source_id: str,
        external_id: str,
        payload: dict[str, Any],
        *,
        url: str | None = None,
        fetched_at: datetime | None = None,
    ):
        if not source_id or not isinstance(source_id, str):
            raise ValueError("source_id must be non-empty str")
        if not external_id or not isinstance(external_id, str):
            raise ValueError("external_id must be non-empty str")
        if not isinstance(payload, dict):
            raise TypeError("payload must be dict")
        if url is not None and not isinstance(url, str):
            raise TypeError("url must be str or None")

        self._source_id = source_id.strip()
        self._external_id = external_id.strip()
        self._payload = dict(payload)
        self._url = url
        self._fetched_at = fetched_at or datetime.now(timezone.utc)
        self._frozen = True

    @property
    def source_id(self) -> str:
        return self._source_id

    @property
    def external_id(self) -> str:
        return self._external_id

    @property
    def payload(self) -> dict[str, Any]:
        return self._payload

    @property
    def url(self) -> str | None:
        return self._url

    @property
    def fetched_at(self) -> datetime:
        return self._fetched_at

    @property
    def natural_key(self) -> tuple[str, str]:
        return self._source_id, self._external_id

    def copy_with(
        self,
        *,
        payload: dict[str, Any] | None = None,
        url: str | None | type(...) = ...,
        fetched_at: datetime | None = None,
    ) -> "RawListing":
        return RawListing(
            source_id=self.source_id,
            external_id=self.external_id,
            payload=dict(payload) or dict(self._payload),
            url=url or self._url,
            fetched_at=fetched_at or self._fetched_at,
        )

    def __setattr__(self, key, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Cannot modify frozen RawListing: {key}={value}")
        super().__setattr__(key, value)

    def __repr__(self) -> str:
        return f"RawListing(source='{self._source_id}', external_id='{self._external_id}', url='{self._url}')"


if __name__ == "__main__":
    raw_listing = RawListing(
        source_id="source123",
        external_id="ext456",
        payload={"key": "value"},
        url="http://example.com/listing/123",
        fetched_at=datetime(2023, 10, 1, 12, 0, tzinfo=timezone.utc),
    )
    raw_listing._url = "http://example.com/new_listing/123"

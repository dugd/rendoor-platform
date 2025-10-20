from typing import Protocol, Mapping, Any, AsyncIterable

from core.domain.ingest import RawListing, Page

from .http import HttpPolicy, HttpTransport, HttpClient


class Provider(Protocol):
    """Provider interface for searching and iterating over listings."""

    async def search(
        self, filters: Mapping[str, Any] = None, cursor: str | int | None = None
    ) -> Page: ...
    async def iter(self, ids: list[str]) -> AsyncIterable[RawListing]: ...


__all__ = [
    "HttpPolicy",
    "HttpTransport",
    "HttpClient",
    "Provider",
]

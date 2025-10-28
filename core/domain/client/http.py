from dataclasses import dataclass

from core.domain.ingest import RawListing


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    params: dict[str, str] | None = None
    data: dict[str, str] | None = None
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class Response:
    status: int
    content: bytes
    url: str
    headers: dict[str, str]


@dataclass(frozen=True)
class Page:
    items: list[str]
    next_cursor: str | int | None = None
    meta: dict[str, str] | None = None


@dataclass(frozen=True)
class ListingResult:
    """
    A result of listings fetched from the provider.
    """

    listing: RawListing
    next_cursor: str | None


__all__ = [
    "Request",
    "Response",
    "Page",
    "ListingResult",
]

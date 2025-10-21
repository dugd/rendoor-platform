from typing import Protocol, AsyncIterable, Mapping, Any

from core.domain.ingest import RawListing, Page


class ListingProvider(Protocol):
    """
    Provider interface for extracting listings from external sources (Extract phase).

    This is the high-level interface that abstracts away the details of how
    listings are fetched from different sources (dom.ria, olx, etc.).
    """

    async def search(
        self, filters: Mapping[str, Any] | None = None, cursor: str | int | None = None
    ) -> Page:
        """
        Search for listings and return paginated results.

        Args:
            filters: Optional search filters specific to the provider
            cursor: Optional pagination cursor/offset

        Returns:
            Page containing listing IDs and pagination info
        """
        ...

    async def fetch(self, ids: list[str]) -> AsyncIterable[RawListing]:
        """
        Fetch full listing data by IDs.

        Args:
            ids: List of external listing IDs to fetch

        Yields:
            RawListing objects containing raw data from the source
        """
        ...

    @property
    def source_code(self) -> str:
        """
        Returns the source code identifier (e.g., 'domria', 'olx').
        """
        ...


__all__ = [
    "ListingProvider",
]

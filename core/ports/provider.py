from typing import Protocol, AsyncIterable

from core.domain.client import ListingResult


class ListingProvider(Protocol):
    """
    Provider interface for extracting listings from external sources.
    """

    async def fetch(
        self,
        cursor: str | None = None,
    ) -> AsyncIterable[ListingResult]:
        """Fetch listings from the external source."""
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

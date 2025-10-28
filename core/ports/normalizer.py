from typing import Protocol

from core.domain.listing import Listing
from core.domain.ingest import RawListing


class ListingNormalizer(Protocol):
    """
    Normalizer interface for converting RawListing to Listing.
    """

    async def normalize(self, raw: RawListing) -> Listing:
        """
        Transform a RawListing into a normalized Listing.
        """
        ...

    @property
    def source_code(self) -> str:
        """
        Returns the source code identifier this normalizer handles (e.g., 'domria', 'olx').
        """
        ...


__all__ = [
    "ListingNormalizer",
]

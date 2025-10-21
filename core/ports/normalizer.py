from typing import Protocol

from core.domain.listing import Listing
from core.domain.ingest import RawListing


class ListingNormalizer(Protocol):
    """
    Normalizer interface for converting RawListing to Listing (Transform phase).

    This is the high-level interface that abstracts away the details of how
    raw listings from different sources are transformed into normalized Listing objects.
    """

    async def normalize(self, raw: RawListing) -> Listing:
        """
        Transform a RawListing into a normalized Listing.

        Args:
            raw: Raw listing data from external source

        Returns:
            Normalized Listing domain object

        Raises:
            ValueError: If the raw listing cannot be normalized
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

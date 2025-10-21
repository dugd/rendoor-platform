from typing import Protocol

from core.domain.listing import Listing
from core.domain.ingest import RawListing


class ListingLoader(Protocol):
    """
    Loader interface for persisting listings to storage (Load phase).

    This is the high-level interface that abstracts away the details of how
    listings are stored (database, file system, etc.).
    """

    async def save_raw(self, raw: RawListing) -> RawListing:
        """
        Save a raw listing to storage.

        Args:
            raw: RawListing to save

        Returns:
            RawListing with updated ID if it was newly created
        """
        ...

    async def save_listing(self, listing: Listing) -> Listing:
        """
        Save a normalized listing to storage.

        Args:
            listing: Listing to save

        Returns:
            Listing with updated ID and timestamps if it was newly created
        """
        ...

    async def bulk_save_raw(self, raws: list[RawListing]) -> list[RawListing]:
        """
        Save multiple raw listings in bulk for better performance.

        Args:
            raws: List of RawListings to save

        Returns:
            List of RawListings with updated IDs
        """
        ...

    async def bulk_save_listings(self, listings: list[Listing]) -> list[Listing]:
        """
        Save multiple normalized listings in bulk for better performance.

        Args:
            listings: List of Listings to save

        Returns:
            List of Listings with updated IDs and timestamps
        """
        ...


__all__ = [
    "ListingLoader",
]

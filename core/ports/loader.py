from typing import Protocol

from core.domain.listing import Listing
from core.domain.ingest import RawListing


class ListingLoader(Protocol):
    """
    Loader interface for persisting listings to storage.
    """

    async def save_raw(self, raw: RawListing) -> RawListing:
        """
        Save a raw listing to storage.
        """
        ...

    async def save_listing(self, listing: Listing) -> Listing:
        """
        Save a normalized listing to storage.
        """
        ...

    async def bulk_save_raw(self, raws: list[RawListing]) -> list[RawListing]:
        """
        Save multiple raw listings in bulk for better performance.
        """
        ...

    async def bulk_save_listings(self, listings: list[Listing]) -> list[Listing]:
        """
        Save multiple normalized listings in bulk for better performance.
        """
        ...


__all__ = [
    "ListingLoader",
]

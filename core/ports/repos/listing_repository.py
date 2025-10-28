from typing import Protocol

from core.domain.listing import Listing


class IListingRepository(Protocol):
    """Repository interface for listings"""

    async def save(self, listing: Listing) -> Listing:
        """Save or update a listing"""
        ...

    async def get_by_id(self, listing_id: int) -> Listing | None:
        """Get listing by ID"""
        ...

    async def find_by_fingerprint(self, fingerprint: str) -> list[Listing]:
        """Find listings by fingerprint"""
        ...

    async def find_by_source_and_external_id(
        self, source_code: str, external_id: str
    ) -> Listing | None:
        """Find listing by source code and external ID"""
        ...

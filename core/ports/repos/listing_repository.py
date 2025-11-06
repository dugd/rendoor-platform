from typing import Protocol
from datetime import datetime
from dataclasses import dataclass

from core.domain.listing import Listing


@dataclass
class ListingStatsByCity:
    """Statistics for listings grouped by city"""

    city: str
    count: int
    avg_price: float | None
    min_price: float | None
    max_price: float | None


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

    async def get_stats_by_city(
        self,
        only_active: bool = True,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[ListingStatsByCity]:
        """Get statistics grouped by city"""
        ...

    async def get_total_count(
        self,
        city: str | None = None,
        only_active: bool = True,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of listings with optional filters"""
        ...

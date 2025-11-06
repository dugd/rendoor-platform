from typing import Protocol
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from core.domain.user import Filter


@dataclass
class FilterCityStats:
    """Statistics about filters by city"""

    city: str
    count: int


class IFilterRepository(Protocol):
    """Repository interface for user filters"""

    async def save(self, filter_obj: Filter) -> Filter:
        """Save or update a filter"""
        ...

    async def get_by_id(self, filter_id: UUID) -> Filter | None:
        """Get filter by ID"""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[Filter]:
        """Get all filters for a user"""
        ...

    async def get_active_filter(self, user_id: UUID) -> Filter | None:
        """Get the active filter for a user"""
        ...

    async def delete(self, filter_id: UUID) -> None:
        """Delete a filter"""
        ...

    async def get_popular_cities(
        self,
        limit: int = 10,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> list[FilterCityStats]:
        """Get most popular cities in filters"""
        ...

    async def get_total_count(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of filters"""
        ...

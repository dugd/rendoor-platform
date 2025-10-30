from typing import Protocol
from uuid import UUID

from core.domain.user import Filter


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

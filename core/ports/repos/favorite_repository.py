from typing import Protocol
from uuid import UUID

from core.domain.user import Favorite


class IFavoriteRepository(Protocol):
    """Repository interface for user favorites"""

    async def save(self, favorite: Favorite) -> Favorite:
        """Save a favorite"""
        ...

    async def delete(self, favorite_uuid: UUID) -> None:
        """Delete a favorite by UUID"""
        ...

    async def get_by_id(self, favorite_uuid: UUID) -> Favorite | None:
        """Get favorite by UUID"""
        ...

    async def get_by_user_and_listing(
        self, user_id: UUID, listing_id: UUID
    ) -> Favorite | None:
        """Get favorite by user and listing IDs"""
        ...

    async def get_user_favorites(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Favorite]:
        """Get all favorites for a user with pagination"""
        ...

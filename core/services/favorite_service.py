from uuid import UUID

from core.domain.user import Favorite
from core.ports.repos import IFavoriteRepository


class FavoriteService:
    """Service for favorite-related business logic"""

    def __init__(self, favorite_repository: IFavoriteRepository):
        self._favorite_repo = favorite_repository

    async def add_to_favorites(self, user_id: UUID, listing_id: UUID) -> Favorite:
        """
        Add a listing to user's favorites.

        Raises:
            ValueError: If the listing is already in favorites
        """
        # Check if already exists
        existing = await self._favorite_repo.get_by_user_and_listing(
            user_id, listing_id
        )
        if existing:
            raise ValueError("Listing is already in favorites")

        # Create new favorite
        new_favorite = Favorite(tg_user_id=user_id, listing_id=listing_id)

        return await self._favorite_repo.save(new_favorite)

    async def remove_from_favorites(self, user_id: UUID, listing_id: UUID) -> None:
        """
        Remove a listing from user's favorites.

        Raises:
            ValueError: If the listing is not in favorites
        """
        existing = await self._favorite_repo.get_by_user_and_listing(
            user_id, listing_id
        )
        if not existing:
            raise ValueError("Listing is not in favorites")

        await self._favorite_repo.delete(existing.uuid)

    async def get_user_favorites(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Favorite]:
        """
        Get all favorites for a user with pagination.

        Args:
            user_id: User's UUID
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Favorite entities, ordered by creation date (newest first)
        """
        return await self._favorite_repo.get_user_favorites(user_id, limit, offset)

    async def is_favorited(self, user_id: UUID, listing_id: UUID) -> bool:
        """
        Check if a listing is in user's favorites.

        Returns:
            True if the listing is favorited, False otherwise
        """
        existing = await self._favorite_repo.get_by_user_and_listing(
            user_id, listing_id
        )
        return existing is not None

    async def get_favorite_by_id(self, favorite_uuid: UUID) -> Favorite | None:
        """
        Get a favorite by its UUID.
        """
        return await self._favorite_repo.get_by_id(favorite_uuid)

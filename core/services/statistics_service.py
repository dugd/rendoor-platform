"""Statistics service for aggregating user and platform metrics"""

from uuid import UUID
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from core.ports.repos import (
    IUserRepository,
    IListingRepository,
    IFilterRepository,
    ISubscriptionRepository,
    IFavoriteRepository,
)
from core.ports.repos.listing_repository import ListingStatsByCity
from core.ports.repos.filter_repository import FilterCityStats


@dataclass
class UserStatistics:
    """Personal user statistics"""

    filters_count: int
    favorites_count: int
    active_subscription: bool


@dataclass
class PlatformStatistics:
    """Platform-wide statistics"""

    total_users: int
    active_users: int
    premium_users: int
    total_listings: int
    active_listings: int
    total_filters: int
    active_subscriptions: int
    total_favorites: int
    listings_by_city: list[ListingStatsByCity]
    popular_cities: list[FilterCityStats]


class StatisticsService:
    """Service for aggregating and computing statistics"""

    def __init__(
        self,
        user_repo: IUserRepository,
        listing_repo: IListingRepository,
        filter_repo: IFilterRepository,
        subscription_repo: ISubscriptionRepository,
        favorite_repo: IFavoriteRepository,
    ):
        self._user_repo = user_repo
        self._listing_repo = listing_repo
        self._filter_repo = filter_repo
        self._subscription_repo = subscription_repo
        self._favorite_repo = favorite_repo

    async def get_user_statistics(self, user_id: UUID) -> UserStatistics:
        """Get personalized statistics for a user"""
        # User's filters
        filters = await self._filter_repo.get_by_user_id(user_id)

        # User's favorites
        favorites = await self._favorite_repo.get_user_favorites(
            user_id, limit=10000, offset=0
        )

        # If user has active subscription
        active_sub = await self._subscription_repo.get_active_by_user_id(user_id)

        return UserStatistics(
            filters_count=len(filters),
            favorites_count=len(favorites),
            active_subscription=active_sub is not None,
        )

    async def get_platform_statistics(
        self,
        period_days: int | None = None,
    ) -> PlatformStatistics:
        """Get platform-wide statistics"""
        # Calculate date filter if period is specified
        created_after = None
        if period_days:
            created_after = datetime.now(timezone.utc) - timedelta(days=period_days)

        # User statistics (all-time)
        user_stats = await self._user_repo.get_user_stats()

        active_users = await self._user_repo.get_active_users_count(since=created_after)

        # Listing statistics
        total_listings = await self._listing_repo.get_total_count(
            created_after=created_after,
        )
        active_listings = await self._listing_repo.get_total_count(
            created_after=created_after,
        )

        # Listings by city (top 5)
        listings_by_city = await self._listing_repo.get_stats_by_city(
            created_after=created_after,
        )
        # Limit to top 5 cities
        listings_by_city = listings_by_city[:5]

        # Popular cities by filters (top 5)
        popular_cities = await self._filter_repo.get_popular_cities(
            limit=5,
            created_after=created_after,
        )

        # Filter count
        total_filters = await self._filter_repo.get_total_count(
            created_after=created_after,
        )

        # Subscription statistics
        active_subs = await self._subscription_repo.get_active_count(
            created_after=created_after,
        )

        # Favorites count
        total_favorites = await self._favorite_repo.get_total_count(
            created_after=created_after,
        )

        return PlatformStatistics(
            total_users=user_stats.total_count,
            active_users=active_users,
            premium_users=user_stats.premium_count,
            total_listings=total_listings,
            active_listings=active_listings,
            total_filters=total_filters,
            active_subscriptions=active_subs,
            total_favorites=total_favorites,
            listings_by_city=listings_by_city,
            popular_cities=popular_cities,
        )

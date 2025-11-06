from typing import Protocol
from uuid import UUID
from datetime import datetime

from core.domain.notify import Subscription


class ISubscriptionRepository(Protocol):
    """Repository interface for subscriptions"""

    async def save(self, subscription: Subscription) -> Subscription:
        """Save or update a subscription"""
        ...

    async def get_by_id(self, subscription_id: UUID) -> Subscription | None:
        """Get subscription by ID"""
        ...

    async def get_by_filter_id(self, filter_id: UUID) -> list[Subscription]:
        """Get all subscriptions for a filter"""
        ...

    async def get_active_by_user_id(self, user_id: UUID) -> Subscription | None:
        """Get the active subscription for a user (via filter relationship)"""
        ...

    async def get_by_user_id(self, user_id: UUID) -> list[Subscription]:
        """Get all subscriptions for a user (via filter relationship)"""
        ...

    async def deactivate_by_user_id(self, user_id: UUID) -> None:
        """Deactivate all active subscriptions for a user"""
        ...

    async def delete(self, subscription_id: UUID) -> None:
        """Delete a subscription"""
        ...

    async def get_active_count(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get count of active subscriptions

        Args:
            created_after: Only count subscriptions created after this datetime (optional)
            created_before: Only count subscriptions created before this datetime (optional)

        Returns:
            Count of active subscriptions across all users
        """
        ...

    async def get_total_count(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> int:
        """Get total count of all subscriptions"""
        ...

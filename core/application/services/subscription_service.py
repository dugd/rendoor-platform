from uuid import UUID

from core.domain.notify import Subscription
from core.ports.repos import ISubscriptionRepository


class SubscriptionService:
    """Service for subscription-related business logic"""

    def __init__(self, subscription_repository: ISubscriptionRepository):
        self._subscription_repo = subscription_repository

    async def activate_subscription(
        self, user_id: UUID, filter_id: UUID, chat_id: int
    ) -> Subscription:
        """
        Activate a subscription for a filter.
        Only one subscription can be active at a time per user.

        Args:
            user_id: User's UUID
            filter_id: Filter UUID to subscribe to
            chat_id: Telegram chat ID for notifications

        Returns:
            The activated subscription
        """
        # First, deactivate any existing active subscriptions for this user
        await self._subscription_repo.deactivate_by_user_id(user_id)

        # Check if a subscription already exists for this filter
        existing_subscriptions = await self._subscription_repo.get_by_filter_id(filter_id)

        if existing_subscriptions:
            # Reactivate the existing subscription
            subscription = existing_subscriptions[0]
            subscription.activate()
            return await self._subscription_repo.save(subscription)

        # Create a new subscription
        new_subscription = Subscription(
            filter_id=filter_id,
            chat_id=chat_id,
            channel="telegram",
            is_active=True,
        )

        return await self._subscription_repo.save(new_subscription)

    async def deactivate_subscription(self, user_id: UUID, filter_id: UUID) -> None:
        """
        Deactivate a subscription for a specific filter.

        Args:
            user_id: User's UUID
            filter_id: Filter UUID to unsubscribe from
        """
        subscriptions = await self._subscription_repo.get_by_filter_id(filter_id)

        for subscription in subscriptions:
            if subscription.is_active:
                subscription.deactivate()
                await self._subscription_repo.save(subscription)

    async def deactivate_all_user_subscriptions(self, user_id: UUID) -> None:
        """
        Deactivate all subscriptions for a user.

        Args:
            user_id: User's UUID
        """
        await self._subscription_repo.deactivate_by_user_id(user_id)

    async def get_active_subscription(self, user_id: UUID) -> Subscription | None:
        """
        Get the active subscription for a user.

        Args:
            user_id: User's UUID

        Returns:
            Active subscription or None
        """
        return await self._subscription_repo.get_active_by_user_id(user_id)

    async def get_user_subscriptions(self, user_id: UUID) -> list[Subscription]:
        """
        Get all subscriptions for a user (both active and inactive).

        Args:
            user_id: User's UUID

        Returns:
            List of subscriptions
        """
        return await self._subscription_repo.get_by_user_id(user_id)

    async def get_subscription_by_id(self, subscription_id: UUID) -> Subscription | None:
        """
        Get a subscription by ID.

        Args:
            subscription_id: Subscription UUID

        Returns:
            Subscription or None
        """
        return await self._subscription_repo.get_by_id(subscription_id)

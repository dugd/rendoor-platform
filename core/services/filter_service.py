from uuid import UUID
from typing import TYPE_CHECKING

from core.domain.user import Filter
from core.domain.user.value import LocationFilter, PriceFilter, ApartmentFilter
from core.ports.repos import IFilterRepository

if TYPE_CHECKING:
    from .subscription_service import SubscriptionService


class FilterService:
    """Service for filter-related business logic"""

    def __init__(
        self,
        filter_repository: IFilterRepository,
        subscription_service: "SubscriptionService | None" = None,
    ):
        self._filter_repo = filter_repository
        self._subscription_service = subscription_service

    async def create_filter(
        self,
        user_id: UUID,
        name: str,
        city: str,
        price_min: float | None = None,
        price_max: float | None = None,
        room_count: int | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
    ) -> Filter:
        """Create a new filter"""
        location_filter = LocationFilter(city=city)

        price_filter = None
        if price_min is not None or price_max is not None:
            price_filter = PriceFilter(price_min=price_min, price_max=price_max)

        apartment_filter = None
        if room_count is not None or area_min is not None or area_max is not None:
            apartment_filter = ApartmentFilter(
                room_count=room_count,
                area_min=area_min,
                area_max=area_max,
            )

        new_filter = Filter(
            user_id=user_id,
            name=name,
            location_filter=location_filter,
            price_filter=price_filter,
            apartment_filter=apartment_filter,
        )

        return await self._filter_repo.save(new_filter)

    async def get_filter_by_id(self, filter_id: UUID) -> Filter | None:
        return await self._filter_repo.get_by_id(filter_id)

    async def get_user_filters(self, user_id: UUID) -> list[Filter]:
        return await self._filter_repo.get_by_user_id(user_id)

    async def get_active_filter(self, user_id: UUID) -> Filter | None:
        return await self._filter_repo.get_active_filter(user_id)

    async def update_filter(self, filter_obj: Filter) -> Filter:
        return await self._filter_repo.save(filter_obj)

    async def delete_filter(self, filter_id: UUID) -> None:
        await self._filter_repo.delete(filter_id)

    async def activate_filter(
        self, user_id: UUID, filter_id: UUID, chat_id: int
    ) -> None:
        """
        Activate a filter for the user by creating/activating a subscription.
        Only one filter can be active at a time per user.

        Args:
            user_id: User's UUID
            filter_id: Filter UUID to activate
            chat_id: Telegram chat ID for notifications
        """
        if self._subscription_service is None:
            raise RuntimeError(
                "SubscriptionService not injected into FilterService. "
                "Cannot activate filter without subscription service."
            )

        await self._subscription_service.activate_subscription(
            user_id=user_id, filter_id=filter_id, chat_id=chat_id
        )

    async def deactivate_filter(self, user_id: UUID, filter_id: UUID) -> None:
        """
        Deactivate a filter for the user by deactivating its subscription.

        Args:
            user_id: User's UUID
            filter_id: Filter UUID to deactivate
        """
        if self._subscription_service is None:
            raise RuntimeError(
                "SubscriptionService not injected into FilterService. "
                "Cannot deactivate filter without subscription service."
            )

        await self._subscription_service.deactivate_subscription(
            user_id=user_id, filter_id=filter_id
        )

from uuid import UUID

from core.domain.user import Filter
from core.domain.user.value import LocationFilter, PriceFilter, ApartmentFilter
from core.ports.repos import IFilterRepository


class FilterService:
    """Service for filter-related business logic"""

    def __init__(self, filter_repository: IFilterRepository):
        self._filter_repo = filter_repository

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

    async def activate_filter(self, user_id: UUID, filter_id: UUID) -> None:
        """
        Activate a filter for the user.
        Only one filter can be active at a time per user.

        Note: This is a placeholder for UI integration.
        Actual subscription logic will be implemented later.
        """
        # TODO: Implement subscription activation logic
        # 1. Deactivate any existing active subscriptions for this user
        # 2. Create or activate subscription for the given filter
        pass

    async def deactivate_filter(self, user_id: UUID, filter_id: UUID) -> None:
        """
        Deactivate a filter for the user.

        Note: This is a placeholder for UI integration.
        Actual subscription logic will be implemented later.
        """
        # TODO: Implement subscription deactivation logic
        # Set is_active=False for the subscription
        pass

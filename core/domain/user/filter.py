from .value import PriceFilter, LocationFilter, ApartmentFilter


class Filter:
    __slots__ = (
        "_id",
        "_user_id",
        "_location_filter",
        "_price_filter",
        "_apartment_filter",
    )

    def __init__(
        self,
        _id: int,
        user_id: int,
        location_filter: LocationFilter,
        price_filter: PriceFilter | None = None,
        apartment_filter: ApartmentFilter | None = None,
    ):
        self._id = _id
        self._user_id = user_id
        self._location_filter = location_filter
        self._price_filter = price_filter
        self._apartment_filter = apartment_filter

    @property
    def id(self) -> int:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def location_filter(self) -> LocationFilter:
        return self._location_filter

    @property
    def price_filter(self) -> PriceFilter | None:
        return self._price_filter

    @property
    def apartment_filter(self) -> ApartmentFilter | None:
        return self._apartment_filter

    def __repr__(self):
        return (
            f"Filter(id={self._id}, user_id={self._user_id}, "
            f"location_filter={self._location_filter}, "
            f"price_filter={self._price_filter}, "
            f"apartment_filter={self._apartment_filter})"
        )

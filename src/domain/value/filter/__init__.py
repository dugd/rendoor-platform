from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class PriceFilter:
    price_min: float | None
    price_max: float | None


@dataclass(frozen=True, eq=True)
class LocationFilter:
    city: str


@dataclass(frozen=True, eq=True)
class ApartmentFilter:
    room_count: int | None
    area_min: float | None
    area_max: float | None

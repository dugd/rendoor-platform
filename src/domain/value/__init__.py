from dataclasses import dataclass

from .filter import PriceFilter, LocationFilter, ApartmentFilter


@dataclass(frozen=True, eq=True)
class Money:
    amount: float
    currency: str


@dataclass(frozen=True, eq=True)
class GeoLocation:
    latitude: float
    longitude: float


@dataclass(frozen=True, eq=True)
class Address:
    state: str
    city: str
    street: str | None
    zip_code: str | None


@dataclass(frozen=True, eq=True)
class Image:
    url: str
    description: str | None


__all__ = [
    "Money",
    "GeoLocation",
    "Address",
    "Image",
    "PriceFilter",
    "LocationFilter",
    "ApartmentFilter",
]

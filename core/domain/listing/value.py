from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, eq=True)
class Money:
    amount: float
    currency: str  # 'UAH', 'USD', 'EUR'

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")


@dataclass(frozen=True, eq=True)
class GeoLocation:
    latitude: float
    longitude: float

    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")


@dataclass(frozen=True, eq=True)
class Address:
    country: str
    state: str  # region
    city: str
    district: str | None = None
    street: str | None = None
    building: str | None = None
    zip_code: str | None = None

    def to_display_string(self) -> str:
        """Returns address for display"""
        parts = [self.city]
        if self.district:
            parts.append(self.district)
        if self.street:
            parts.append(self.street)
        if self.building:
            parts.append(f"building {self.building}")
        return ", ".join(parts)

    def to_search_key(self) -> str:
        """Returns normalized key for duplicate search"""
        parts = [
            self.city.lower().strip(),
            (self.district or "").lower().strip(),
            (self.street or "").lower().strip(),
            (self.building or "").lower().strip(),
        ]
        return "|".join(p for p in parts if p)


@dataclass(frozen=True, eq=True)
class Image:
    url: str
    order: int

    def __post_init__(self):
        if not self.url:
            raise ValueError("Image URL cannot be empty")
        if self.order < 0:
            raise ValueError("Order cannot be negative")


@dataclass(frozen=True, eq=True)
class ContactInfo:
    """Owner contact information"""

    phone: str | None = None
    telegram: str | None = None
    viber: str | None = None
    whatsapp: str | None = None
    email: str | None = None

    def has_any_contact(self) -> bool:
        return any([self.phone, self.telegram, self.viber, self.whatsapp, self.email])

    def get_primary_contact(self) -> tuple[str, str] | None:
        """Returns (type, value) of the first available contact"""
        if self.phone:
            return ("phone", self.phone)
        if self.telegram:
            return ("telegram", self.telegram)
        if self.viber:
            return ("viber", self.viber)
        if self.whatsapp:
            return ("whatsapp", self.whatsapp)
        if self.email:
            return ("email", self.email)
        return None


OwnerType = Literal["private", "realtor", "agency", "unknown"]


@dataclass(frozen=True, eq=True)
class OwnerInfo:
    """Owner information from listing"""

    name: str | None = None
    owner_type: OwnerType = "unknown"
    contact: ContactInfo | None = None

    def is_realtor(self) -> bool:
        return self.owner_type in ("realtor", "agency")


ListingStatus = Literal["active", "rented", "removed", "duplicate", "archived"]


__all__ = [
    "Money",
    "GeoLocation",
    "Address",
    "Image",
    "OwnerType",
    "OwnerInfo",
    "ContactInfo",
    "ListingStatus",
]

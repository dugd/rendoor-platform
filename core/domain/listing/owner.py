from datetime import datetime

from .value import OwnerType, ContactInfo


class Owner:
    """
    Owner aggregate that unifies listings from different sources.

    Created automatically when processing listings through fingerprinting
    of contact data (phone, email, etc.).
    """

    def __init__(
        self,
        owner_id: int,
        fingerprint: str,  # hash of contact data
        name: str | None = None,
        owner_type: OwnerType = "unknown",
        contact: ContactInfo | None = None,
        rating: float = 0.0,
        listing_count: int = 0,
        verified: bool = False,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id = owner_id
        self.fingerprint = fingerprint
        self.name = name
        self.owner_type = owner_type
        self.contact = contact
        self.rating = rating
        self.listing_count = listing_count
        self.verified = verified
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def update_info(
        self,
        *,
        name: str | None = None,
        owner_type: OwnerType | None = None,
        contact: ContactInfo | None = None,
    ) -> None:
        """Updates owner information"""
        if name:
            self.name = name
        if owner_type:
            self.owner_type = owner_type
        if contact:
            self.contact = contact
        self.updated_at = datetime.now()

    def increment_listing_count(self) -> None:
        """Increments listing counter"""
        self.listing_count += 1
        self.updated_at = datetime.now()

    def decrement_listing_count(self) -> None:
        """Decrements listing counter"""
        if self.listing_count > 0:
            self.listing_count -= 1
        self.updated_at = datetime.now()

    def update_rating(self, new_rating: float) -> None:
        """Updates owner rating"""
        if not 0 <= new_rating <= 5:
            raise ValueError("Rating must be between 0 and 5")
        self.rating = new_rating
        self.updated_at = datetime.now()

    def mark_verified(self) -> None:
        """Marks owner as verified"""
        self.verified = True
        self.updated_at = datetime.now()

    def is_suspicious(self) -> bool:
        """Checks if owner is suspicious"""
        return (
            self.owner_type in ("realtor", "agency")
            or self.listing_count > 10  # too many listings
            or self.rating < 2.0
        )

    def __repr__(self) -> str:
        return f"Owner(id={self.id}, name='{self.name}', type={self.owner_type}, listings={self.listing_count})"


def generate_owner_fingerprint(contact: ContactInfo) -> str:
    """
    Generates owner fingerprint based on contact data.

    Used to unify listings from one owner
    from different sources.
    """
    import hashlib

    parts = []

    if contact.phone:
        # Remove all non-digit characters
        normalized_phone = "".join(c for c in contact.phone if c.isdigit())
        parts.append(f"phone:{normalized_phone}")

    if contact.email:
        parts.append(f"email:{contact.email.lower().strip()}")

    if contact.telegram:
        parts.append(f"tg:{contact.telegram.lower().strip().lstrip('@')}")

    if not parts:
        raise ValueError("At least one contact method is required for fingerprinting")

    key = "|".join(sorted(parts))
    return hashlib.sha256(key.encode()).hexdigest()[:32]


__all__ = [
    "Owner",
    "generate_owner_fingerprint",
]

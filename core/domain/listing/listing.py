from datetime import datetime, timezone
import hashlib

from .value import (
    Money,
    Address,
    GeoLocation,
    Image,
    OwnerInfo,
    ListingStatus,
)


class Listing:
    """
    Rental listing aggregate.

    This is a normalized listing created from RawListing
    and contains all necessary information for the system to work.
    """

    def __init__(
        self,
        listing_id: int,
        source_code: str,
        external_id: str,
        url: str,
        title: str,
        *,
        owner_id: int | None = None,
        owner_info: OwnerInfo | None = None,
        price: Money | None = None,
        address: Address | None = None,
        location: GeoLocation | None = None,
        room_count: int | None = None,
        area: float | None = None,
        floor: int | None = None,
        total_floors: int | None = None,
        description: str | None = None,
        photos: list[Image] | None = None,
        status: ListingStatus = "active",
        is_verified: bool = False,
        view_count: int = 0,
        fingerprint: str | None = None,
        first_seen_at: datetime | None = None,
        last_seen_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        if not source_code:
            raise ValueError("source_code is required")
        if not external_id:
            raise ValueError("external_id is required")
        if not url:
            raise ValueError("url is required")
        if not title:
            raise ValueError("title is required")

        self.id = listing_id
        self.source_code = source_code.strip().lower()
        self.external_id = external_id.strip()
        self.url = url.strip()
        self.title = title.strip()

        self.owner_id = owner_id
        self.owner_info = owner_info

        self.price = price
        self.address = address
        self.location = location

        self.room_count = room_count
        self.area = area
        self.floor = floor
        self.total_floors = total_floors
        self.description = description
        self.photos = photos or []

        self.status = status
        self.is_verified = is_verified
        self.view_count = view_count

        self.fingerprint = fingerprint or self._generate_fingerprint()

        now = datetime.now(timezone.utc)
        self.first_seen_at = first_seen_at or now
        self.last_seen_at = last_seen_at or now
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    @property
    def natural_key(self) -> tuple[str, str]:
        """Unique key within the source"""
        return self.source_code, self.external_id

    def _generate_fingerprint(self) -> str:
        """
        Generates fingerprint for duplicate detection.

        Uses a combination of address, room count, area, and floor.
        """
        parts = []

        if self.address:
            parts.append(self.address.to_search_key())

        if self.room_count is not None:
            parts.append(f"rooms:{self.room_count}")

        if self.area is not None:
            # Round to 1 decimal for similar areas
            parts.append(f"area:{round(self.area, 1)}")

        if self.floor is not None:
            parts.append(f"floor:{self.floor}")

        if not parts:
            # If no data for fingerprint, use source + external_id
            parts = [self.source_code, self.external_id]

        key = "|".join(parts)
        return hashlib.sha256(key.encode()).hexdigest()[:32]

    def assign_owner(self, owner_id: int) -> None:
        """Links listing to owner"""
        self.owner_id = owner_id
        self.updated_at = datetime.now(timezone.utc)

    def update_price(self, new_price: Money) -> None:
        """Updates price (will create entry in price history)"""
        if self.price != new_price:
            self.price = new_price
            self.updated_at = datetime.now(timezone.utc)

    def mark_seen(self) -> None:
        """Marks that the listing was found again (still active)"""
        self.last_seen_at = datetime.now(timezone.utc)
        self.updated_at = self.last_seen_at

    def change_status(self, new_status: ListingStatus) -> None:
        """Changes listing status"""
        if self.status != new_status:
            self.status = new_status
            self.updated_at = datetime.now(timezone.utc)

    def mark_verified(self) -> None:
        """Marks as verified"""
        self.is_verified = True
        self.updated_at = datetime.now(timezone.utc)

    def increment_views(self) -> None:
        """Increments view counter"""
        self.view_count += 1
        self.updated_at = datetime.now(timezone.utc)

    def is_from_realtor(self) -> bool:
        """Checks if from realtor"""
        return self.owner_info is not None and self.owner_info.is_realtor()

    def is_duplicate_of(self, other: "Listing") -> bool:
        """Checks if this listing is a duplicate of another"""
        # If fingerprint matches - it's a duplicate
        if self.fingerprint == other.fingerprint:
            return True

        # Additional check by address and main parameters
        if self.address and other.address:
            same_address = self.address.to_search_key() == other.address.to_search_key()
            same_params = (
                self.room_count == other.room_count
                and self.floor == other.floor
                and abs((self.area or 0) - (other.area or 0)) < 5  # tolerance 5 m²
            )
            return same_address and same_params

        return False

    def __repr__(self) -> str:
        price_str = (
            f"{self.price.amount} {self.price.currency}" if self.price else "N/A"
        )
        return f"Listing(id={self.id}, title='{self.title[:30]}...', price={price_str}, status={self.status})"

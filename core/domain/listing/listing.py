from uuid import UUID, uuid4
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
        source_code: str,
        external_id: str,
        url: str,
        title: str,
        *,
        uuid: UUID | None = None,
        external_owner_id: str | None = None,
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
        fingerprint: str | None = None,
        is_archived: bool = False,
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

        self.uuid = uuid or uuid4()
        self.source_code = source_code.strip().lower()
        self.external_id = external_id.strip()
        self.url = url.strip()
        self.title = title.strip()

        self.external_owner_id = external_owner_id
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

        self.fingerprint = fingerprint or self._internal_generate_fingerprint()

        self.is_archived = is_archived

        self.first_seen_at = first_seen_at  # might be not nullable
        self.last_seen_at = last_seen_at
        self.created_at = created_at or updated_at
        self.updated_at = updated_at or created_at

    @property
    def natural_key(self) -> tuple[str, str]:
        """Unique key within the source"""
        return self.source_code, self.external_id

    def _internal_generate_fingerprint(self) -> str:
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

    def update_price(self, new_price: Money) -> None:
        """Updates price (will create entry in price history (may be later))"""
        if self.price != new_price:
            self.price = new_price
            self.updated_at = datetime.now(timezone.utc)

    def mark_seen(self) -> None:
        """Marks that the listing was found again (still active)"""
        self.last_seen_at = datetime.now(timezone.utc)

    def change_status(self, new_status: ListingStatus) -> None:
        """Changes listing status"""
        if self.status != new_status:
            self.status = new_status

    def mark_verified(self) -> None:
        """Marks as verified"""
        self.is_verified = True

    def is_from_realtor(self) -> bool:
        """Checks if from realtor"""
        return self.owner_info is not None and self.owner_info.is_realtor()

    def archive(self) -> None:
        """Archives the listing"""
        if not self.is_archived:
            self.is_archived = True

    def __repr__(self) -> str:
        price_str = (
            f"{self.price.amount} {self.price.currency}" if self.price else "N/A"
        )
        return f"Listing(id={self.uuid}, title='{self.title[:30]}...', price={price_str}, status={self.status})"

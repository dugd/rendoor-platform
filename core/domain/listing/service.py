from typing import Protocol
from .listing import Listing
from .owner import Owner


class DuplicateDetectionService:
    """Service for duplicate detection"""

    def find_duplicates(
        self,
        listing: Listing,
        candidates: list[Listing],
    ) -> list[Listing]:
        """Finds duplicates among candidates"""
        duplicates = []

        for candidate in candidates:
            if listing.id != candidate.id and listing.is_duplicate_of(candidate):
                duplicates.append(candidate)

        return duplicates

    def merge_duplicates(
        self,
        primary: Listing,
        duplicates: list[Listing],
    ) -> Listing:
        """
        Merges duplicates, keeping primary as the main listing.

        All duplicates get status 'duplicate'.
        """
        for duplicate in duplicates:
            duplicate.change_status("duplicate")

        # Update first_seen_at to the earliest date
        earliest_seen = min(
            [primary.first_seen_at] + [d.first_seen_at for d in duplicates]
        )
        if earliest_seen < primary.first_seen_at:
            primary.first_seen_at = earliest_seen

        return primary


class OwnerLinkingService:
    """Service for linking listings to owners"""

    def link_listing_to_owner(
        self,
        listing: Listing,
        owner: Owner,
    ) -> None:
        """Links listing to owner"""
        listing.assign_owner(owner.id)
        owner.increment_listing_count()


class IListingRepository(Protocol):
    """Repository interface for listings"""

    def save(self, listing: Listing) -> Listing: ...
    def find_by_id(self, listing_id: int) -> Listing | None: ...
    def find_by_fingerprint(self, fingerprint: str) -> list[Listing]: ...
    def find_by_source_and_external_id(
        self, source_code: str, external_id: str
    ) -> Listing | None: ...


class IOwnerRepository(Protocol):
    """Repository interface for owners"""

    def save(self, owner: Owner) -> Owner: ...
    def find_by_id(self, owner_id: int) -> Owner | None: ...
    def find_by_fingerprint(self, fingerprint: str) -> Owner | None: ...

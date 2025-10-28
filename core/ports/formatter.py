from typing import Protocol
from core.domain.listing import Listing


class ListingFormatter(Protocol):
    """Interface for formatting listing data."""

    def format_listing(self, listing: Listing) -> dict:
        """
        Format the listing into a dictionary representation.

        Returns:
            dict: Formatted listing data (text, keyboard, etc.).
        """
        ...

    def format_short(self, listing: Listing) -> str:
        """Short text representation of the listing."""
        ...

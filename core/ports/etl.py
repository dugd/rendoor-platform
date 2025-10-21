from typing import Protocol, Mapping, Any, AsyncIterable
from dataclasses import dataclass

from core.domain.listing import Listing
from core.domain.ingest import RawListing


@dataclass
class ETLResult:
    """Result of an ETL pipeline run."""

    total_fetched: int
    total_normalized: int
    total_loaded: int
    total_failed: int
    errors: list[str]


class ListingETLPipeline(Protocol):
    """
    High-level ETL Pipeline interface for collecting listings from any source.

    This is the main interface to interact with. It orchestrates the
    Extract-Transform-Load process.
    """

    async def run(
        self,
        filters: Mapping[str, Any] | None = None,
        max_pages: int | None = None,
        save_raw: bool = True,
    ) -> ETLResult:
        """
        Run the full ETL pipeline: Extract -> Transform -> Load.

        Args:
            filters: Optional filters to apply when searching for listings
            max_pages: Maximum number of pages to fetch (None = unlimited)
            save_raw: Whether to save raw listings to storage (default: True)

        Returns:
            ETLResult with statistics about the run
        """
        ...

    async def extract(
        self,
        filters: Mapping[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> AsyncIterable[RawListing]:
        """
        Extract raw listings from the source (Extract phase only).

        Args:
            filters: Optional filters to apply when searching
            max_pages: Maximum number of pages to fetch

        Yields:
            RawListing objects from the source
        """
        ...

    async def transform(self, raws: list[RawListing]) -> list[Listing]:
        """
        Transform raw listings to normalized listings (Transform phase only).

        Args:
            raws: List of raw listings to transform

        Returns:
            List of normalized Listing objects
        """
        ...

    async def load(
        self, listings: list[Listing], raws: list[RawListing] | None = None
    ) -> None:
        """
        Load normalized listings to storage (Load phase only).

        Args:
            listings: List of normalized listings to save
            raws: Optional list of raw listings to save
        """
        ...

    @property
    def source_code(self) -> str:
        """
        Returns the source code identifier (e.g., 'domria', 'olx').
        """
        ...


__all__ = [
    "ListingETLPipeline",
    "ETLResult",
]

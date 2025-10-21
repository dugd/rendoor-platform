from typing import AsyncIterable, Mapping, Any

from core.ports import (
    ListingProvider,
    ListingNormalizer,
    ListingLoader,
    ETLResult,
)
from core.domain.listing import Listing
from core.domain.ingest import RawListing


class DomRiaETLPipeline:
    """
    Concrete ETL Pipeline implementation for DomRia source.
    """

    def __init__(
        self,
        provider: ListingProvider,
        normalizer: ListingNormalizer,
        loader: ListingLoader,
    ):
        """
        Initialize the ETL pipeline.

        Args:
            provider: Provider for extracting raw listings
            normalizer: Normalizer for transforming raw to normalized listings
            loader: Loader for persisting listings to storage
        """
        self._provider = provider
        self._normalizer = normalizer
        self._loader = loader

    @property
    def source_code(self) -> str:
        """Returns the source code identifier."""
        return self._provider.source_code

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
        total_fetched = 0
        total_normalized = 0
        total_loaded = 0
        total_failed = 0
        errors: list[str] = []

        try:
            # Extract: Get raw listings from source
            raw_listings: list[RawListing] = []
            async for raw in self.extract(filters=filters, max_pages=max_pages):
                raw_listings.append(raw)
                total_fetched += 1

            # Transform: Normalize raw listings
            normalized_listings = await self.transform(raw_listings)
            total_normalized = len(normalized_listings)

            # Load: Save to storage
            await self.load(
                listings=normalized_listings,
                raws=raw_listings if save_raw else None,
            )
            total_loaded = len(normalized_listings)

        except Exception as e:
            total_failed += 1
            errors.append(f"Pipeline error: {str(e)}")

        return ETLResult(
            total_fetched=total_fetched,
            total_normalized=total_normalized,
            total_loaded=total_loaded,
            total_failed=total_failed,
            errors=errors,
        )

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
        page_count = 0
        cursor = None

        while True:
            # Check if reached max pages
            if max_pages is not None and page_count >= max_pages:
                break

            page = await self._provider.search(filters=filters, cursor=cursor)

            if not page.items:
                break

            async for raw_listing in self._provider.fetch(page.items):
                yield raw_listing

            cursor = page.next_cursor
            page_count += 1

            if cursor is None:
                break

    async def transform(self, raws: list[RawListing]) -> list[Listing]:
        """
        Transform raw listings to normalized listings (Transform phase only).

        Args:
            raws: List of raw listings to transform

        Returns:
            List of normalized Listing objects
        """
        listings: list[Listing] = []

        for raw in raws:
            try:
                listing = await self._normalizer.normalize(raw)
                listings.append(listing)
            except Exception as e:
                # Log error
                print(f"Failed to normalize listing {raw.external_id}: {e}")

        return listings

    async def load(
        self, listings: list[Listing], raws: list[RawListing] | None = None
    ) -> None:
        """
        Load normalized listings to storage (Load phase only).

        Args:
            listings: List of normalized listings to save
            raws: Optional list of raw listings to save
        """
        # Save raw if requested
        if raws:
            await self._loader.bulk_save_raw(raws)

        await self._loader.bulk_save_listings(listings)

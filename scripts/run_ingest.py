"""
Complete ETL ingestion script for DomRia listings.

1. Extract: Fetch raw listings from DomRia
2. Transform: Normalize raw data to domain model
3. Load: Save to database
"""

import asyncio
from loguru import logger

from core.adapters.providers.domria import DomRiaProvider
from core.adapters.normalizers.domria import DomRiaNormalizer
from core.adapters.loaders import DatabaseListingLoader
from core.infra.http.builder import build_async_client
from core.infra.db.context import init_db, get_session, shutdown_db
from core.infra.repos.outbox_repository import OutboxRepository


async def main():
    """Run the complete ETL pipeline."""
    logger.info("Starting DomRia ETL pipeline...")

    # Init db connection
    init_db()

    try:
        client = await build_async_client("https://dom.ria.com")
        logger.info("HTTP client built successfully")

        provider = DomRiaProvider(
            client=client,
            max_listings=20,
        )
        normalizer = DomRiaNormalizer()

        async with get_session() as session:
            loader = DatabaseListingLoader(session, OutboxRepository(session))

            logger.info("ETL pipeline initialized")

            # Run the pipeline
            raw_listings = []
            listings = []
            failed_ids = []
            async for listing_result in provider.fetch():
                raw_listing = listing_result.listing
                raw_listings.append(raw_listing)
                try:
                    normalized_listing = await normalizer.normalize(raw_listing)
                    listings.append(normalized_listing)
                except Exception as e:
                    failed_id = getattr(raw_listing, "uuid", None)
                    failed_ids.append(failed_id)
                    logger.error(
                        f"Failed to process listing ID: {failed_id}, Error: {e}"
                    )

            # Stats before saving
            total_raw = len(raw_listings)
            total_normalized = len(listings)
            total_failed = len(failed_ids)
            logger.info(
                f"ETL stats - Fetched: {total_raw}, Normalized: {total_normalized}, Failed: {total_failed}"
            )

            # Persist data
            if raw_listings:
                await loader.bulk_save_raw(raw_listings)
                logger.info(f"Saved {total_raw} raw listings to database")
            if listings:
                await loader.bulk_save_listings(listings)
                logger.info(f"Saved {total_normalized} normalized listings to database")

            # Detailed failure log (ids)
            if failed_ids:
                logger.warning(f"Failed listing IDs: {failed_ids}")

            logger.success("ETL pipeline completed successfully!")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise

    finally:
        # Clean up
        await shutdown_db()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())

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
from core.adapters.etl.domria_pipeline import DomRiaETLPipeline
from core.infra.http.builder import build_async_client
from core.infra.db.context import init_db, get_session, shutdown_db


async def main():
    """Run the complete ETL pipeline."""
    logger.info("Starting DomRia ETL pipeline...")

    # Init db connection
    init_db()

    try:
        client = await build_async_client("https://dom.ria.com")
        logger.info("HTTP client built successfully")

        provider = DomRiaProvider(client=client)
        normalizer = DomRiaNormalizer()

        async for session in get_session():
            loader = DatabaseListingLoader(session)

            pipeline = DomRiaETLPipeline(
                provider=provider,
                normalizer=normalizer,
                loader=loader,
            )

            logger.info("ETL pipeline initialized")

            # Run the pipeline
            result = await pipeline.run(
                max_pages=1,
                save_raw=True,
            )

            # Display results
            logger.info("=" * 60)
            logger.info("ETL Pipeline Results:")
            logger.info(f"  Total Fetched:    {result.total_fetched}")
            logger.info(f"  Total Normalized: {result.total_normalized}")
            logger.info(f"  Total Loaded:     {result.total_loaded}")
            logger.info(f"  Total Failed:     {result.total_failed}")

            if result.errors:
                logger.error("Errors encountered:")
                for error in result.errors:
                    logger.error(f"  - {error}")

            logger.info("=" * 60)
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

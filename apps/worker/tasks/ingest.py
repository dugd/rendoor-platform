from loguru import logger

from core.adapters import DomRiaProvider, DomRiaNormalizer, DatabaseListingLoader
from core.infra.db import get_session
from core.infra.http.builder import build_async_client

from apps.worker.app import celery
from apps.worker.lifespan import get_loop


@celery.task(bind=True)
def run_ingest(self, max_listings: int = 10):
    """Run the full ingest ETL pipeline"""
    loop = get_loop()

    async def _run():
        client = await build_async_client("https://dom.ria.com")
        logger.info("HTTP client built successfully")

        provider = DomRiaProvider(client=client, max_listings=max_listings)
        normalizer = DomRiaNormalizer()

        async with get_session() as session:
            loader = DatabaseListingLoader(session)

            logger.info("ETL pipeline initialized")

            # Run the pipeline
            try:
                raw_listings = []
                listings = []
                async for listing_result in provider.fetch():
                    raw_listing = listing_result.listing
                    raw_listings.append(raw_listing)
                    try:
                        normalized_listing = await normalizer.normalize(raw_listing)
                        listings.append(normalized_listing)
                    except Exception as e:
                        logger.error(
                            f"Failed to process listing ID: {raw_listing.uuid}, Error: {e}"
                        )

                await loader.bulk_save_raw(raw_listings)
                loaded = await loader.bulk_save_listings(listings)
            except Exception as e:
                logger.error(f"ETL pipeline failed: {e}")
                raise

            logger.success("ETL pipeline completed successfully!")

        return {
            "total_fetched": len(raw_listings),
            "total_normalized": len(listings),
            "total_loaded": len(loaded),
            "total_failed": len(raw_listings) - len(listings),
        }

    result = loop.run_until_complete(_run())
    return result

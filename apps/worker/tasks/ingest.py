from core.config import get_settings

from ..app import celery
from ..di import get_container


@celery.task(bind=True)
def run_ingest(self, pages: int | None = None):
    """Run the full ingest ETL pipeline"""
    container = get_container()
    loop = container.get_or_create_loop()

    async def _run():
        etl_pipeline = await container.domria_etl_pipeline
        result = await etl_pipeline.run(
            max_pages=pages if pages else 1,
            save_raw=get_settings().SAVE_RAW_LISTINGS,
        )
        return result

    result = loop.run_until_complete(_run())
    return {
        "total_fetched": result.total_fetched,
        "total_normalized": result.total_normalized,
        "total_loaded": result.total_loaded,
        "total_failed": result.total_failed,
        "errors": result.errors,
    }

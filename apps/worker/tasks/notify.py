import asyncio

from core.domain.notify import ChatId
from core.config import get_settings

from ..app import celery
from ..di import get_container


@celery.task(bind=True)
def send_notification(self, message: str):
    """Send notification to admin chat"""

    async def _send():
        chat_id = get_settings().TELEGRAM_ADMIN_CHAT_ID

        container = get_container()
        notifier = container.notifier
        await notifier.send_text(ChatId(chat_id), message)

    asyncio.run(_send())


@celery.task(bind=True)
def send_listing_notification(self, listing_id: int):
    """Send listing notification to admin chat"""

    async def _send():
        chat_id = get_settings().TELEGRAM_ADMIN_CHAT_ID

        container = get_container()
        notifier = container.notifier
        listing_repo = await container.listing_repository()

        listing = await listing_repo.get_by_id(listing_id)
        if not listing:
            raise ValueError(f"Listing with id {listing_id} not found")

        await notifier.send_listing(ChatId(chat_id), listing)

    asyncio.run(_send())

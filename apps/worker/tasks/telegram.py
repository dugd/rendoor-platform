from core.domain.notify import ChatId
from core.config import get_settings

from ..app import celery
from ..di import get_container
from ..lifespan import get_loop


async def notify_admin_text(container, message: str):
    chat_id = get_settings().TELEGRAM_ADMIN_CHAT_ID
    notifier = container.notifier
    await notifier.send_text(ChatId(chat_id), message)


async def notify_admin_listing(container, listing_id: int):
    chat_id = get_settings().TELEGRAM_ADMIN_CHAT_ID
    notifier = container.notifier
    async with container.listing_repository() as listing_repo:
        listing = await listing_repo.get_by_id(listing_id)
        if not listing:
            raise ValueError(f"Listing with id {listing_id} not found")

        await notifier.send_listing(ChatId(chat_id), listing)


def _run_coro(container, coro):
    loop = get_loop()
    return loop.run_until_complete(coro)


@celery.task(bind=True)
def send_notification(self, message: str):
    container = get_container()
    _run_coro(container, notify_admin_text(container, message))


@celery.task(bind=True)
def send_listing_notification(self, listing_id: int):
    container = get_container()
    _run_coro(container, notify_admin_listing(container, listing_id))

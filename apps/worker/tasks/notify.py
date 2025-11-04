from uuid import UUID
from loguru import logger

from core.domain.notify import ChatId

from ..app import celery, container
from ..lifespan import get_loop


@celery.task(bind=True, max_retries=3)
def send_notification(self, chat_id: int, listing_id: str):
    """
    Send notification to user via Telegram.

    Args:
        chat_id: Telegram chat ID to send notification to
        listing_id: UUID of the listing to send
    """
    loop = get_loop()

    async def _send():
        async with container.uow() as uow:
            # Load listing from database
            listing = await uow.listings.get_by_id(UUID(listing_id))
            if not listing:
                logger.warning(f"Listing {listing_id} not found, skipping notification")
                return

            # Get notifier from container services
            notifier = container.services.notifier

            try:
                # Send notification via Telegram
                message_id = await notifier.send_listing(
                    ChatId(chat_id),
                    listing
                )
                logger.info(
                    f"Sent notification: listing_id={listing_id}, "
                    f"chat_id={chat_id}, message_id={message_id.value}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to send notification: listing_id={listing_id}, "
                    f"chat_id={chat_id}, error={e}"
                )
                # Retry the task with exponential backoff
                raise self.retry(
                    exc=e,
                    countdown=60 * (2 ** self.request.retries)
                )

    return loop.run_until_complete(_send())

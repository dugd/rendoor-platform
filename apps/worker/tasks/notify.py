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

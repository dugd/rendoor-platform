from aiogram import Bot

from core.ports.notifier import Notifier
from core.domain.listing import Listing
from core.domain.notify import ChatId, MessageId


class TelegramNotifier(Notifier):
    """Telegram Notifier implementation.

    Args:
        bot (Bot): Aiogram Bot instance.
        admin_chat_id (ChatId, optional): Default admin chat ID. Defaults to None.
    """

    def __init__(self, bot: Bot, admin_chat_id: ChatId = None):
        self._bot = bot
        self._admin_chat_id = admin_chat_id

    async def send_listing(self, chat_id: ChatId, listing: Listing) -> MessageId:
        """Send listing info message. (temporary implementation)"""
        text = (
            f"🏠 <b>{listing.title}</b>\n"
            f"💰 Price: {listing.price}\n"
            f"📍 Location: {listing.location}\n"
            f'🔗 <a href="{listing.url}">View Listing</a>'
        )
        message = await self._bot.send_message(
            chat_id.value,
            text,
            parse_mode="HTML",
        )
        return MessageId(message.message_id)

    async def send_text(self, chat_id: ChatId, text: str) -> MessageId:
        """Send raw text message."""
        message = await self._bot.send_message(chat_id.value, text)
        return MessageId(message.message_id)

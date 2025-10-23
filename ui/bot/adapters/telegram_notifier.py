from aiogram import Bot

from core.ports.formatter import ListingFormatter
from core.domain.listing import Listing
from core.domain.notify import ChatId, MessageId


class TelegramNotifier:
    """Telegram Notifier implementation.

    Args:
        bot (Bot): Aiogram Bot instance.
        admin_chat_id (ChatId, optional): Default admin chat ID. Defaults to None.
    """

    def __init__(
        self, bot: Bot, formatter: ListingFormatter, admin_chat_id: ChatId = None
    ):
        self._bot = bot
        self._formatter = formatter
        self._admin_chat_id = admin_chat_id

    async def send_listing(self, chat_id: ChatId, listing: Listing) -> MessageId:
        """Send listing info message using ListingFormatter."""
        formatted = self._formatter.format_listing(listing)

        # if formatted.get("photos"):
        #     result = await self._bot.send_media_group(
        #         chat_id=chat_id.value, media=formatted["photos"]
        #     )
        #     msg_id = result[0].message_id
        # else:
        result = await self._bot.send_message(
            chat_id=chat_id.value,
            text=formatted["text"],
            reply_markup=formatted.get("keyboard"),
            parse_mode="HTML",
        )
        msg_id = result.message_id

        return MessageId(msg_id)

    async def send_text(self, chat_id: ChatId, text: str) -> MessageId:
        """Send raw text message."""
        message = await self._bot.send_message(chat_id.value, text)
        return MessageId(message.message_id)

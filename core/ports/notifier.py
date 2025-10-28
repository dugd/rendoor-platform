from typing import Protocol

from core.domain.listing import Listing
from core.domain.notify import ChatId, MessageId


class Notifier(Protocol):
    async def send_listing(self, chat_id: ChatId, listing: Listing) -> MessageId:
        """Send listing info"""
        ...

    async def send_text(self, chat_id: ChatId, text: str) -> MessageId:
        """Send raw text"""
        ...

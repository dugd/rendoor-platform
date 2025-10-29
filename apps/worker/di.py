from typing import AsyncGenerator
from contextlib import asynccontextmanager

from aiogram import Bot

from core.config import get_settings
from core.ports.notifier import Notifier
from core.ports.repos import IListingRepository
from core.domain.notify import ChatId
from core.infra.db.context import get_session
from core.infra.telegram import get_bot
from core.infra.repos import ListingRepository
from adapters.notifier import TelegramNotifier
from adapters.formatter import TelegramListingFormatter


class Container:
    def __init__(self):
        self._bot = None
        self._formatter = None
        self._loop = None

    @property
    def bot(self) -> Bot:
        """Lazy initialization of bot"""
        return get_bot()

    @property
    def formatter(self) -> TelegramListingFormatter:
        """Lazy initialization of formatter"""
        if not self._formatter:
            self._formatter = TelegramListingFormatter()
        return self._formatter

    @property
    def notifier(self) -> Notifier:
        """Initialization of notifier"""
        return TelegramNotifier(
            bot=self.bot,
            formatter=self.formatter,
            admin_chat_id=ChatId(get_settings().TELEGRAM_ADMIN_CHAT_ID),
        )

    @asynccontextmanager
    async def listing_repository(self) -> AsyncGenerator[IListingRepository, None]:
        """Create a new listing repository instance with a fresh session"""
        async with get_session() as session:
            yield ListingRepository(session)


_container: Container | None = None


def get_container() -> Container:
    global _container
    if not _container:
        _container = Container()
    return _container

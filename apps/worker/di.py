from aiogram import Bot

from core.config import get_settings
from core.ports.notifier import Notifier
from core.ports.repos import IListingRepository
from core.domain.notify import ChatId
from core.infra.db.context import get_sessionmaker
from core.infra.repos import ListingRepository
from ui.bot.adapters.telegram_notifier import TelegramNotifier
from ui.bot.formatters.listing_formatter import TelegramListingFormatter


class Container:
    def __init__(self):
        self._bot = None
        self._notifier = None
        self._formatter = None

    @property
    def bot(self) -> Bot:
        if not self._bot:
            self._bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN)
        return self._bot

    @property
    def formatter(self) -> TelegramListingFormatter:
        if not self._formatter:
            self._formatter = TelegramListingFormatter()
        return self._formatter

    @property
    def notifier(self) -> Notifier:
        if not self._notifier:
            self._notifier = TelegramNotifier(
                bot=self.bot,
                formatter=self.formatter,
                admin_chat_id=ChatId(get_settings().TELEGRAM_ADMIN_CHAT_ID),
            )
        return self._notifier

    async def listing_repository(self) -> IListingRepository:
        """Create a new listing repository instance with a fresh session"""
        sessionmaker = get_sessionmaker()
        session = sessionmaker()
        return ListingRepository(session)


_container: Container | None = None


def get_container() -> Container:
    global _container
    if not _container:
        _container = Container()
    return _container

import asyncio
from aiogram import Bot

from core.config import get_settings
from core.ports.notifier import Notifier
from core.ports.repos import IListingRepository
from core.domain.notify import ChatId
from core.infra.db.context import get_sessionmaker
from core.infra.repos import ListingRepository
from core.adapters.providers.domria import DomRiaProvider
from core.adapters.normalizers.domria import DomRiaNormalizer
from core.adapters.loaders.database import DatabaseListingLoader
from core.adapters.etl.domria_pipeline import DomRiaETLPipeline
from core.infra.http.builder import build_async_client
from ui.bot.adapters.telegram_notifier import TelegramNotifier
from ui.bot.formatters.listing_formatter import TelegramListingFormatter


class Container:
    def __init__(self):
        self._bot = None
        self._formatter = None
        self._loop = None

    def get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop for this worker process"""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    @property
    def bot(self) -> Bot:
        """Lazy initialization of bot with proper event loop"""
        if self._bot is None:
            self.get_or_create_loop()
            self._bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN)
        return self._bot

    @property
    def formatter(self) -> TelegramListingFormatter:
        if not self._formatter:
            self._formatter = TelegramListingFormatter()
        return self._formatter

    @property
    def notifier(self) -> Notifier:
        return TelegramNotifier(
            bot=self.bot,
            formatter=self.formatter,
            admin_chat_id=ChatId(get_settings().TELEGRAM_ADMIN_CHAT_ID),
        )

    @property
    async def domria_etl_pipeline(self):
        client = await build_async_client("https://dom.ria.com")
        provider = DomRiaProvider(client)
        normalizer = DomRiaNormalizer()
        sessionmaker = get_sessionmaker()
        session = sessionmaker()
        loader = DatabaseListingLoader(session)

        return DomRiaETLPipeline(provider, normalizer, loader)

    async def listing_repository(self) -> IListingRepository:
        """Create a new listing repository instance with a fresh session"""
        sessionmaker = get_sessionmaker()
        session = sessionmaker()
        return ListingRepository(session)

    def cleanup(self):
        """Cleanup resources when worker shuts down"""
        if self._bot and self._loop and not self._loop.is_closed():
            self._loop.run_until_complete(self._bot.session.close())
            self._bot = None


_container: Container | None = None


def get_container() -> Container:
    global _container
    if not _container:
        _container = Container()
    return _container

from aiogram import Bot

from core.config import get_settings
from core.ports.notifier import Notifier
from core.domain.notify import ChatId
from ui.bot.adapters.telegram_notifier import TelegramNotifier


class Container:
    def __init__(self):
        self._bot = None
        self._notifier = None

    @property
    def bot(self) -> Bot:
        if not self._bot:
            self._bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN)
        return self._bot

    @property
    def notifier(self) -> Notifier:
        if not self._notifier:
            self._notifier = TelegramNotifier(
                bot=self.bot,
                admin_chat_id=ChatId(get_settings().TELEGRAM_ADMIN_CHAT_ID),
            )
        return self._notifier


_container: Container | None = None


def get_container() -> Container:
    global _container
    if not _container:
        _container = Container()
    return _container

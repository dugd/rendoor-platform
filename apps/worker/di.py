from __future__ import annotations
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Callable

from aiogram import Bot

from core.config import get_settings, Settings
from core.ports.notifier import Notifier
from core.ports.uow import IUnitOfWork
from core.infra.telemetry.logger import configure_logger
from core.infra.db import init_db, shutdown_db
from core.infra.db.context import get_sessionmaker
from core.infra.telegram import init_bot, shutdown_bot, get_bot
from core.adapters.formatter import TelegramListingFormatter
from core.adapters.notifier import TelegramNotifier
from core.infra.uow import uow_factory
from core.domain.notify import ChatId


@dataclass(slots=True)
class Infra:
    settings: Settings
    bot: Bot
    session_factory: Callable[..., AsyncGenerator]  # get_session


@dataclass(slots=True)
class Services:
    formatter: TelegramListingFormatter
    notifier: Notifier

    @staticmethod
    def build(infra: Infra) -> "Services":
        fmt = TelegramListingFormatter()
        notifier = TelegramNotifier(
            bot=infra.bot,
            formatter=fmt,
            admin_chat_id=ChatId(infra.settings.TELEGRAM_ADMIN_CHAT_ID),
        )
        return Services(formatter=fmt, notifier=notifier)


class AppContainer:
    """
    Один в процесі. Ясні межі:
      - start(): ініціалізує важкі ресурси
      - stop(): закриває їх
      - uow(): віддає task-scope контекст з сесією і репозиторіями
    """

    def __init__(self) -> None:
        self._infra: Infra | None = None
        self._services: Services | None = None

    # ---------- lifecycle ----------
    async def start(self) -> None:
        configure_logger("celery-app")

        settings = get_settings()
        init_db(dsn=settings.get_postgres_dsn("asyncpg"))
        init_bot(settings.TELEGRAM_BOT_TOKEN)

        infra = Infra(
            settings=settings,
            bot=get_bot(),
            session_factory=get_sessionmaker(),
        )
        self._infra = infra
        self._services = Services.build(infra)

    async def stop(self) -> None:
        await shutdown_db()
        await shutdown_bot()

        self._infra = None
        self._services = None

    # ---------- accessors ----------
    @property
    def infra(self) -> Infra:
        assert self._infra is not None, "Container not started"
        return self._infra

    @property
    def services(self) -> Services:
        assert self._services is not None, "Container not started"
        return self._services

    # ---------- UoW ----------
    @asynccontextmanager
    async def uow(self) -> AsyncGenerator["IUnitOfWork", None]:
        """
        Task-scope. Новий сеанс на кожний вхід. Репозиторії прив'язані до нього.
        """
        async with self.infra.session_factory() as session:
            async with uow_factory(session) as uow:
                yield uow

import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import from_url

from core.infra.telemetry.logger import configure_logger
from core.config import get_settings
from core.infra.telegram import init_bot
from core.infra.db import init_db, shutdown_db

from .handlers import get_main_router
from .middlewares import (
    DatabaseMiddleware,
    DependencyInjectionMiddleware,
    UserTrackerMiddleware,
)

logger = configure_logger("bot-app")


async def main():
    settings = get_settings()

    logger.info("Configuring Telegram bot...")

    bot = init_bot(settings.TELEGRAM_BOT_TOKEN)

    init_db(dsn=settings.get_postgres_dsn("asyncpg"))
    redis = from_url(settings.BOT_STORAGE_URL)
    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_bot_id=True),
    )
    dp = Dispatcher(storage=storage)

    main_router = get_main_router()

    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(DependencyInjectionMiddleware())
    dp.update.middleware(UserTrackerMiddleware())

    dp.include_router(main_router)

    try:
        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        logger.info("Stopping Telegram bot...")

        await bot.session.close()
        await shutdown_db()


if __name__ == "__main__":
    asyncio.run(main())

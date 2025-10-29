import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import from_url

from core.infra.telemetry.logger import configure_logger
from core.config import get_settings
from core.infra.telegram import init_bot

from .handlers import common_router

logger = configure_logger("bot-app")

bot = init_bot(get_settings().TELEGRAM_BOT_TOKEN)
redis = from_url(get_settings().BOT_STORAGE_URL)
storage = RedisStorage(
    redis=redis,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)
dp = Dispatcher(storage=storage)

dp.include_router(common_router)


async def main():
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())

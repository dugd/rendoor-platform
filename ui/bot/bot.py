import asyncio
import logging

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from redis.asyncio import from_url

from core.config import get_settings
from core.infra.telegram import init_bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = init_bot(get_settings().TELEGRAM_BOT_TOKEN)
redis = from_url(get_settings().REDIS_URL)
storage = RedisStorage(
    redis=redis,
    key_builder=DefaultKeyBuilder(with_bot_id=True),
)
dp = Dispatcher(storage=storage)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привіт, {message.from_user.first_name}!\n\n"
        "Використовуй /help для списку команд."
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступні команди:\n\n"
        "/start - Початок роботи\n"
        "/help - Ця довідка\n"
        "/ping - Перевірка зв'язку"
    )


@dp.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("Pong!")


async def main():
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())

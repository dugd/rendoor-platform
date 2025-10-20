import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=get_settings().TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


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

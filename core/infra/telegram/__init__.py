from aiogram import Bot
from core.config import get_settings


_bot: Bot | None = None


def init_bot(token: str | None = None) -> Bot:
    """Initialize and return the global Telegram Bot instance"""
    settings = get_settings()

    global _bot
    if _bot is not None:
        raise RuntimeError("Bot is already initialized")
    _bot = Bot(token=token or settings.TELEGRAM_BOT_TOKEN)

    return _bot


async def shutdown_bot() -> None:
    """Close the global Telegram Bot instance"""
    global _bot
    if _bot is not None:
        await _bot.session.close()
        _bot = None


def get_bot() -> Bot:
    """Return a Telegram Bot instance"""
    if _bot is None:
        raise RuntimeError(
            "Bot is not initialized. Call init_bot() in your entrypoint."
        )

    return _bot


__all__ = [
    "init_bot",
    "shutdown_bot",
    "get_bot",
]

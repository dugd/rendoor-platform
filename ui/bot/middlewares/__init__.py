from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, User

from core.infra.db import get_session
from core.domain.user import TgUser
from ui.bot.dependencies import DIContainer


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        async with get_session() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise


class DependencyInjectionMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get("session")
        if session:
            data["user_service"] = DIContainer.get_user_service(session)
            data["filter_service"] = DIContainer.get_filter_service(session)
            data["subscription_service"] = DIContainer.get_subscription_service(session)
            data["favorite_service"] = DIContainer.get_favorite_service(session)
            data["listing_repository"] = DIContainer.get_listing_repository(session)
            data["statistics_service"] = DIContainer.get_statistics_service(session)

        return await handler(event, data)


class UserTrackerMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        tg_user = None
        chat_id = None

        if event.message:
            tg_user = event.message.from_user
            chat_id = event.message.chat.id
        elif event.callback_query:
            tg_user = event.callback_query.from_user
            chat_id = (
                event.callback_query.message.chat.id
                if event.callback_query.message
                else None
            )
        elif event.inline_query:
            tg_user = event.inline_query.from_user
            # Inline queries don't have chat_id, skip user tracking

        if tg_user and chat_id:
            session = data.get("session")
            if session:
                domain_user = await self.upsert_user(tg_user, chat_id, session)
                # Inject user and user_service into handler data
                data["user"] = domain_user

        return await handler(event, data)

    async def upsert_user(self, tg_user: User, chat_id: int, session) -> TgUser:
        user_service = DIContainer.get_user_service(session)

        domain_user = await user_service.get_or_create_user(
            tg_user_id=tg_user.id,
            tg_chat_id=chat_id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            is_premium=tg_user.is_premium or False,
        )

        return domain_user


__all__ = [
    "DatabaseMiddleware",
    "DependencyInjectionMiddleware",
    "UserTrackerMiddleware",
]

from datetime import datetime
from uuid import UUID

from core.domain.user import TgUser
from core.ports.repos import IUserRepository


class UserService:
    """Service for user-related business logic"""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def get_or_create_user(
        self,
        tg_user_id: int,
        tg_chat_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_premium: bool = False,
    ) -> TgUser:
        """Get existing user or create new one"""
        # Try to get existing user
        user = await self._user_repo.get_by_tg_user_id(tg_user_id)

        if user:
            # Update user info if changed
            user_updated = False
            if (
                username != user.username
                or first_name != user.first_name
                or last_name != user.last_name
            ):
                user = TgUser(
                    tg_user_id=tg_user_id,
                    tg_chat_id=tg_chat_id,
                    _uuid=user.uuid,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    is_premium=is_premium,
                    last_interaction=datetime.now(),
                    is_active=user.is_active,
                    is_admin=user.is_admin,
                )
                user_updated = True

            # Update last interaction
            if not user_updated:
                await self._user_repo.update_last_interaction(
                    tg_user_id, datetime.now()
                )
            else:
                user = await self._user_repo.save(user)

            return user

        # Create new user
        new_user = TgUser(
            tg_user_id=tg_user_id,
            tg_chat_id=tg_chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_premium=is_premium,
            last_interaction=datetime.now(),
        )

        return await self._user_repo.save(new_user)

    async def get_user_by_id(self, user_id: UUID) -> TgUser | None:
        return await self._user_repo.get_by_id(user_id)

    async def get_user_by_tg_id(self, tg_user_id: int) -> TgUser | None:
        return await self._user_repo.get_by_tg_user_id(tg_user_id)

    async def update_user(self, user: TgUser) -> TgUser:
        return await self._user_repo.save(user)

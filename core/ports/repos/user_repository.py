from typing import Protocol
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from core.domain.user import TgUser


@dataclass
class UserStats:
    """General user statistics"""

    total_count: int
    active_count: int
    premium_count: int


class IUserRepository(Protocol):
    """Repository interface for Telegram users"""

    async def save(self, user: TgUser) -> TgUser:
        """Save or update a user"""
        ...

    async def get_by_id(self, user_id: UUID) -> TgUser | None:
        """Get user by internal UUID"""
        ...

    async def get_by_tg_user_id(self, tg_user_id: int) -> TgUser | None:
        """Get user by Telegram user ID"""
        ...

    async def update_last_interaction(
        self, tg_user_id: int, interaction_time: datetime
    ) -> None:
        """Update user's last interaction timestamp"""
        ...

    async def get_user_stats(
        self,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
    ) -> UserStats:
        """Get general user statistics"""
        ...

    async def get_active_users_count(self, since: datetime) -> int:
        """Count users active since a specific time"""
        ...

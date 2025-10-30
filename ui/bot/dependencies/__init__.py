from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from services.user_service import UserService


class DIContainer:
    """Dependency Injection Container"""

    @staticmethod
    def get_user_repository(session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @staticmethod
    def get_user_service(session: AsyncSession) -> UserService:
        user_repo = DIContainer.get_user_repository(session)
        return UserService(user_repo)


__all__ = [
    "DIContainer",
]

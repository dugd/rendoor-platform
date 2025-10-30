from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.repos import UserRepository, FilterRepository
from core.application.services import UserService, FilterService


class DIContainer:
    """Dependency Injection Container"""

    @staticmethod
    def get_user_repository(session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @staticmethod
    def get_filter_repository(session: AsyncSession) -> FilterRepository:
        return FilterRepository(session)

    @staticmethod
    def get_user_service(session: AsyncSession) -> UserService:
        user_repo = DIContainer.get_user_repository(session)
        return UserService(user_repo)

    @staticmethod
    def get_filter_service(session: AsyncSession) -> FilterService:
        filter_repo = DIContainer.get_filter_repository(session)
        return FilterService(filter_repo)


__all__ = [
    "DIContainer",
]

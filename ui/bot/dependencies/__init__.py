from sqlalchemy.ext.asyncio import AsyncSession

from core.infra.repos import (
    UserRepository,
    FilterRepository,
    SubscriptionRepository,
    FavoriteRepository,
)
from core.services import (
    UserService,
    FilterService,
    SubscriptionService,
    FavoriteService,
)


class DIContainer:
    """Dependency Injection Container"""

    @staticmethod
    def get_user_repository(session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @staticmethod
    def get_filter_repository(session: AsyncSession) -> FilterRepository:
        return FilterRepository(session)

    @staticmethod
    def get_subscription_repository(session: AsyncSession) -> SubscriptionRepository:
        return SubscriptionRepository(session)

    @staticmethod
    def get_favorite_repository(session: AsyncSession) -> FavoriteRepository:
        return FavoriteRepository(session)

    @staticmethod
    def get_user_service(session: AsyncSession) -> UserService:
        user_repo = DIContainer.get_user_repository(session)
        return UserService(user_repo)

    @staticmethod
    def get_subscription_service(session: AsyncSession) -> SubscriptionService:
        subscription_repo = DIContainer.get_subscription_repository(session)
        return SubscriptionService(subscription_repo)

    @staticmethod
    def get_filter_service(session: AsyncSession) -> FilterService:
        filter_repo = DIContainer.get_filter_repository(session)
        subscription_service = DIContainer.get_subscription_service(session)
        return FilterService(filter_repo, subscription_service)

    @staticmethod
    def get_favorite_service(session: AsyncSession) -> FavoriteService:
        favorite_repo = DIContainer.get_favorite_repository(session)
        return FavoriteService(favorite_repo)


__all__ = [
    "DIContainer",
]

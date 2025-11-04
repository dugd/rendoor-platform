from core.domain.user import TgUser
from core.infra.models.user import TgUserORM


class UserMapper:
    """Mapper for converting between TgUser domain entity and TgUserORM"""

    @staticmethod
    def to_domain(orm: TgUserORM) -> TgUser:
        """Convert TgUserORM to TgUser domain entity"""
        return TgUser(
            tg_user_id=orm.tg_user_id,
            tg_chat_id=orm.tg_chat_id,
            _uuid=orm.id,
            username=orm.username,
            first_name=orm.first_name,
            last_name=orm.last_name,
            is_premium=orm.is_premium,
            last_interaction=orm.last_interaction,
            is_active=orm.is_active,
            is_admin=orm.is_admin,
        )

    @staticmethod
    def to_orm(user: TgUser, orm: TgUserORM | None = None) -> TgUserORM:
        """Convert TgUser domain entity to TgUserORM

        Args:
            user: Domain entity
            orm: Existing ORM object to update (optional)
        """
        if orm is None:
            orm = TgUserORM(
                id=user.uuid,
                tg_user_id=user.tg_user_id,
                tg_chat_id=user.tg_chat_id,
            )

        # Update fields
        orm.username = user.username
        orm.first_name = user.first_name
        orm.last_name = user.last_name
        orm.is_premium = user.is_premium
        orm.last_interaction = user.last_interaction
        orm.is_active = user.is_active
        orm.is_admin = user.is_admin

        return orm

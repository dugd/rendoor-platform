from core.domain.user import Favorite
from core.infra.models.user import FavoriteORM


class FavoriteMapper:
    """Mapper for converting between Favorite domain entity and FavoriteORM"""

    @staticmethod
    def to_domain(orm: FavoriteORM) -> Favorite:
        """Convert FavoriteORM to Favorite domain entity"""
        return Favorite(
            tg_user_id=orm.tg_user_id,
            listing_id=orm.listing_id,
            _uuid=orm.id,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(favorite: Favorite, orm: FavoriteORM | None = None) -> FavoriteORM:
        """Convert Favorite domain entity to FavoriteORM"""
        if orm is None:
            # Create new ORM object
            orm = FavoriteORM(
                id=favorite.uuid,
                tg_user_id=favorite.tg_user_id,
                listing_id=favorite.listing_id,
                created_at=favorite.created_at,
            )
        else:
            # Update existing ORM object
            orm.tg_user_id = favorite.tg_user_id
            orm.listing_id = favorite.listing_id
            orm.created_at = favorite.created_at

        return orm

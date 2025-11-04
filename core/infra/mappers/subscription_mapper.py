from core.domain.notify import Subscription
from core.infra.models.notify import SubscriptionORM


class SubscriptionMapper:
    """Mapper for converting between Subscription domain entity and SubscriptionORM"""

    @staticmethod
    def to_domain(orm: SubscriptionORM) -> Subscription:
        """Convert SubscriptionORM to Subscription domain entity

        Args:
            orm: ORM model

        Returns:
            Subscription domain entity
        """
        return Subscription(
            filter_id=orm.filter_id,
            chat_id=orm.chat_id,
            _uuid=orm.id,
            channel=orm.channel,
            is_active=orm.is_active,
            min_interval_sec=orm.min_interval_sec,
            last_sent_at=orm.last_sent_at,
        )

    @staticmethod
    def to_orm(subscription: Subscription, orm: SubscriptionORM | None = None) -> SubscriptionORM:
        """Convert Subscription domain entity to SubscriptionORM

        Args:
            subscription: Domain entity
            orm: Existing ORM object to update (optional)

        Returns:
            SubscriptionORM instance
        """
        if orm is None:
            orm = SubscriptionORM(
                id=subscription.id,
                filter_id=subscription.filter_id,
                channel=subscription.channel,
                chat_id=subscription.chat_id,
                is_active=subscription.is_active,
                min_interval_sec=subscription.min_interval_sec,
                last_sent_at=subscription.last_sent_at,
            )
        else:
            # Update existing ORM
            orm.filter_id = subscription.filter_id
            orm.channel = subscription.channel
            orm.chat_id = subscription.chat_id
            orm.is_active = subscription.is_active
            orm.min_interval_sec = subscription.min_interval_sec
            orm.last_sent_at = subscription.last_sent_at

        return orm

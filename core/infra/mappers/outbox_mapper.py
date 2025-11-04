from typing import Any
from uuid import UUID

from core.domain.notify import OutboxMessage
from core.infra.models.notify import OutboxMessageORM


class OutboxMapper:
    """Mapper for converting between OutboxMessage domain entity and OutboxMessageORM"""

    @staticmethod
    def to_domain(orm: OutboxMessageORM) -> OutboxMessage:
        """Convert OutboxMessageORM to OutboxMessage domain entity

        Args:
            orm: ORM model

        Returns:
            OutboxMessage domain entity
        """
        return OutboxMessage(
            uuid=orm.id,
            message_type=orm.message_type,
            aggregate_id=orm.aggregate_id,
            aggregate_type=orm.aggregate_type,
            payload=orm.payload,
            processed_at=orm.processed_at,
            processing_attempts=orm.processing_attempts,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(message: OutboxMessage, orm: OutboxMessageORM | None = None) -> OutboxMessageORM:
        """Convert OutboxMessage domain entity to OutboxMessageORM

        Args:
            message: Domain entity
            orm: Existing ORM object to update (optional)

        Returns:
            OutboxMessageORM instance
        """
        if orm is None:
            orm = OutboxMessageORM(
                id=message.uuid,
                message_type=message.message_type,
                aggregate_id=message.aggregate_id,
                aggregate_type=message.aggregate_type,
                payload=message.payload,
                processed_at=message.processed_at,
                processing_attempts=message.processing_attempts,
                created_at=message.created_at,
            )
        else:
            # Update existing ORM
            orm.message_type = message.message_type
            orm.aggregate_id = message.aggregate_id
            orm.aggregate_type = message.aggregate_type
            orm.payload = message.payload
            orm.processed_at = message.processed_at
            orm.processing_attempts = message.processing_attempts
            orm.created_at = message.created_at

        return orm

    @staticmethod
    def to_orm_dict(message: OutboxMessage) -> dict[str, Any]:
        """Convert OutboxMessage to dictionary for bulk operations

        Args:
            message: Domain entity

        Returns:
            Dictionary with ORM field names and values
        """
        return {
            "id": message.uuid,
            "message_type": message.message_type,
            "aggregate_id": message.aggregate_id,
            "aggregate_type": message.aggregate_type,
            "payload": message.payload,
            "processed_at": message.processed_at,
            "processing_attempts": message.processing_attempts,
            "created_at": message.created_at,
        }

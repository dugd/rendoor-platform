from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.notify import OutboxMessage
from core.infra.models.notify import OutboxMessageORM
from core.infra.mappers.outbox_mapper import OutboxMapper


class OutboxRepository:
    """SQLAlchemy implementation of outbox message repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, message: OutboxMessage) -> OutboxMessage:
        """Save or update an outbox message"""
        stmt = select(OutboxMessageORM).where(OutboxMessageORM.id == message.uuid)
        result = await self._session.execute(stmt)
        orm_message = result.scalar_one_or_none()

        if orm_message:
            # Update existing message
            OutboxMapper.to_orm(message, orm_message)
        else:
            # Create new message
            orm_message = OutboxMapper.to_orm(message)
            self._session.add(orm_message)

        await self._session.flush()
        await self._session.refresh(orm_message)

        return OutboxMapper.to_domain(orm_message)

    async def bulk_save(self, messages: list[OutboxMessage]) -> list[OutboxMessage]:
        """Save multiple outbox messages in bulk"""
        if not messages:
            return []

        # Prepare bulk insert values using mapper
        values = [OutboxMapper.to_orm_dict(message) for message in messages]

        # Insert all messages
        stmt = insert(OutboxMessageORM).values(values)
        await self._session.execute(stmt)
        await self._session.flush()

        return messages

    async def get_by_id(self, message_id: UUID) -> OutboxMessage | None:
        """Get outbox message by ID"""
        stmt = select(OutboxMessageORM).where(OutboxMessageORM.id == message_id)
        result = await self._session.execute(stmt)
        orm_message = result.scalar_one_or_none()

        if not orm_message:
            return None

        return OutboxMapper.to_domain(orm_message)

    async def get_pending(self, limit: int = 100) -> list[OutboxMessage]:
        """Get pending (unprocessed) outbox messages

        Args:
            limit: Maximum number of messages to fetch

        Returns:
            List of unprocessed OutboxMessage entities
        """
        stmt = (
            select(OutboxMessageORM)
            .where(OutboxMessageORM.processed_at.is_(None))
            .order_by(OutboxMessageORM.created_at)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        orm_messages = result.scalars().all()

        return [OutboxMapper.to_domain(orm) for orm in orm_messages]

    async def mark_processed(self, message_id: UUID) -> None:
        """Mark an outbox message as processed"""
        stmt = (
            update(OutboxMessageORM)
            .where(OutboxMessageORM.id == message_id)
            .values(processed_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def increment_attempts(self, message_id: UUID) -> None:
        """Increment the processing attempts count for a message"""
        stmt = (
            update(OutboxMessageORM)
            .where(OutboxMessageORM.id == message_id)
            .values(processing_attempts=OutboxMessageORM.processing_attempts + 1)
        )
        await self._session.execute(stmt)
        await self._session.flush()

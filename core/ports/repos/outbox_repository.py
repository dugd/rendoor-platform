from typing import Protocol
from uuid import UUID

from core.domain.notify import OutboxMessage


class IOutboxRepository(Protocol):
    """Repository interface for outbox messages"""

    async def save(self, message: OutboxMessage) -> OutboxMessage:
        """Save or update an outbox message"""
        ...

    async def bulk_save(self, messages: list[OutboxMessage]) -> list[OutboxMessage]:
        """Save multiple outbox messages in bulk"""
        ...

    async def get_by_id(self, message_id: UUID) -> OutboxMessage | None:
        """Get outbox message by ID"""
        ...

    async def get_pending(self, limit: int = 100) -> list[OutboxMessage]:
        """Get pending (unprocessed) outbox messages

        Args:
            limit: Maximum number of messages to fetch

        Returns:
            List of unprocessed OutboxMessage entities
        """
        ...

    async def mark_processed(self, message_id: UUID) -> None:
        """Mark an outbox message as processed"""
        ...

    async def increment_attempts(self, message_id: UUID) -> None:
        """Increment the processing attempts count for a message"""
        ...

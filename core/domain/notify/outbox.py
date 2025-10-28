from typing import Any
from uuid import UUID, uuid4
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class OutboxMessage:
    message_type: str
    aggregate_id: UUID
    aggregate_type: str
    payload: dict[str, Any]
    processed_at: datetime | None = None
    processing_attempts: int = 0
    created_at: datetime = datetime.now(timezone.utc)

    uuid: UUID = uuid4()

    def mark_processed(self) -> "OutboxMessage":
        """Marks the message as processed"""
        return self._copy_with(
            processed_at=datetime.now(timezone.utc),
        )

    def increment_attempts(self) -> "OutboxMessage":
        """Increments the processing attempts count"""
        return self._copy_with(
            processing_attempts=self.processing_attempts + 1,
        )

    def _copy_with(
        self,
        *,
        message_type: str | None = None,
        aggregate_id: UUID = None,
        aggregate_type: str | None = None,
        payload: dict[str, Any] | None = None,
        processed_at: datetime | None = None,
        processing_attempts: int | None = None,
    ) -> "OutboxMessage":
        """Creates a copy with updated fields"""
        return OutboxMessage(
            uuid=self.uuid,
            aggregate_type=aggregate_id
            if aggregate_type is not None
            else self.aggregate_type,
            aggregate_id=aggregate_id
            if aggregate_id is not None
            else self.aggregate_id,
            message_type=message_type
            if message_type is not None
            else self.message_type,
            payload=payload if payload is not None else dict(self.payload),
            processed_at=self.processed_at if processed_at is ... else processed_at,
            processing_attempts=self.processing_attempts
            if processing_attempts is not None
            else self.processing_attempts,
            created_at=self.created_at,
        )

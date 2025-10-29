from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    JSON,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from core.infra.db import Model


class OutboxMessageORM(Model):
    __tablename__ = "outbox_messages"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    payload: Mapped[dict] = mapped_column(JSON)  # Message payload as JSON
    aggregate_type: Mapped[str] = mapped_column(
        String(64), index=True
    )  # e.g., "listing"
    aggregate_id: Mapped[UUIDType | None] = mapped_column(
        UUID(as_uuid=True),
    )  # e.g., listing.id
    message_type: Mapped[str] = mapped_column(
        String(64), index=True
    )  # e.g., "listing.created"

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0)

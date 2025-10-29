from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    JSON,
    func,
    text,
    UniqueConstraint,
    CheckConstraint,
    ForeignKey,
    BigInteger,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from core.infra.db import Model

if TYPE_CHECKING:
    from .user import FilterORM


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


class SubscriptionORM(Model):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("filter_id", "channel", "chat_id"),
        CheckConstraint("channel IN ('telegram')", name="ck_subs_channel"),
    )

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    filter_id: Mapped[UUIDType] = mapped_column(
        ForeignKey("filters.id", ondelete="CASCADE"), index=True, nullable=False
    )

    channel: Mapped[str] = mapped_column(String(16), default="telegram")
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )
    min_interval_sec: Mapped[int] = mapped_column(Integer, default=0)
    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    filter: Mapped["FilterORM"] = relationship(
        "FilterORM",
        back_populates="subscriptions",
    )

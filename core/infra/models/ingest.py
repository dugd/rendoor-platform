from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
    JSON,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from core.infra.db import Model

if TYPE_CHECKING:
    from .core import SourceORM


class RawListingORM(Model):
    __tablename__ = "raw_listings"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_code: Mapped[str] = mapped_column(
        ForeignKey("sources.code", ondelete="RESTRICT")
    )
    external_id: Mapped[str] = mapped_column(String(128))

    payload: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[str] = mapped_column(String(16), default="1.0")
    fetch_url: Mapped[str | None] = mapped_column(Text)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    processing_status: Mapped[str] = mapped_column(
        String(32), default="pending", index=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    source: Mapped["SourceORM"] = relationship(back_populates="raw_listings")

    __table_args__ = (
        UniqueConstraint("source_code", "external_id", name="uq_raw_src_ext"),
        Index("ix_raw_status_fetched", "processing_status", "fetched_at"),
    )

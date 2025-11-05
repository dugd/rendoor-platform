from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    func,
    text,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from core.infra.db import Model

if TYPE_CHECKING:
    from .notify import SubscriptionORM


class TgUserORM(Model):
    __tablename__ = "tg_users"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tg_user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )
    tg_chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str | None] = mapped_column(String(64), index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    last_interaction: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    filters: Mapped[list["FilterORM"]] = relationship(
        "FilterORM",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    favorites: Mapped[list["FavoriteORM"]] = relationship(
        "FavoriteORM",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class FilterORM(Model):
    __tablename__ = "filters"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tg_user_id: Mapped[UUIDType] = mapped_column(
        ForeignKey("tg_users.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(128))
    criteria: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["TgUserORM"] = relationship(
        "TgUserORM",
        back_populates="filters",
    )
    subscriptions: Mapped[list["SubscriptionORM"]] = relationship(
        "SubscriptionORM",
        back_populates="filter",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class FavoriteORM(Model):
    __tablename__ = "favorites"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tg_user_id: Mapped[UUIDType] = mapped_column(
        ForeignKey("tg_users.id", ondelete="CASCADE")
    )
    listing_id: Mapped[UUIDType] = mapped_column(
        ForeignKey("tg_users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["TgUserORM"] = relationship("TgUserORM")

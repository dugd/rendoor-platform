from typing import TYPE_CHECKING
from uuid import UUID as UUIDType
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    UniqueConstraint,
    Index,
    JSON,
    Boolean,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from geoalchemy2.types import WKBElement

from core.infra.db import Model

if TYPE_CHECKING:
    from .ingest import RawListingORM


class SourceORM(Model):
    __tablename__ = "sources"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    raw_listings: Mapped[list["RawListingORM"]] = relationship(back_populates="source")
    listings: Mapped[list["ListingORM"]] = relationship(back_populates="source")


class ListingORM(Model):
    __tablename__ = "listings"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    source_code: Mapped[str] = mapped_column(
        ForeignKey("sources.code", ondelete="RESTRICT")
    )
    external_id: Mapped[str] = mapped_column(String(128))

    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(String(64), index=True)

    price_amount: Mapped[float | None] = mapped_column(Float)
    price_currency: Mapped[str | None] = mapped_column(String(8))

    address_country: Mapped[str | None] = mapped_column(String(64))
    address_state: Mapped[str | None] = mapped_column(String(128))
    address_city: Mapped[str | None] = mapped_column(String(128), index=True)
    address_district: Mapped[str | None] = mapped_column(String(128))
    address_street: Mapped[str | None] = mapped_column(String(256))
    address_building: Mapped[str | None] = mapped_column(String(64))
    address_zip: Mapped[str | None] = mapped_column(String(32))

    location: Mapped[WKBElement | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )

    # Apartment details
    room_count: Mapped[int | None] = mapped_column(Integer)
    area: Mapped[float | None] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    total_floors: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    # Owner info from listing
    external_owner_id: Mapped[str | None] = mapped_column(String(128))
    owner_name: Mapped[str | None] = mapped_column(String(256))
    owner_type_declared: Mapped[str | None] = mapped_column(String(32))
    owner_contacts: Mapped[dict | None] = mapped_column(JSON)

    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    listing_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    listing_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped["SourceORM"] = relationship(back_populates="listings")
    photos: Mapped[list["ListingPhotoORM"]] = relationship(
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingPhotoORM.order",
    )

    __table_args__ = (
        UniqueConstraint("source_code", "external_id", name="uq_listing_src_ext"),
        Index("ix_listing_fingerprint_status", "fingerprint", "status"),
        Index("ix_listing_city_price", "address_city", "price_amount"),
        Index("ix_listing_status_updated", "status", "updated_at"),
    )


class ListingPhotoORM(Model):
    __tablename__ = "listing_photos"

    id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    listing_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)

    listing: Mapped["ListingORM"] = relationship(back_populates="photos")

from datetime import datetime
from sqlalchemy import (
    BigInteger,
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
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography
from core.infra.db import Model


class SourceORM(Model):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    raw_listings: Mapped[list["RawListingORM"]] = relationship(back_populates="source")
    listings: Mapped[list["ListingORM"]] = relationship(back_populates="source")


class RawListingORM(Model):
    __tablename__ = "raw_listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT")
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
        UniqueConstraint("source_id", "external_id", name="uq_raw_src_ext"),
        Index("ix_raw_status_fetched", "processing_status", "fetched_at"),
    )


class OwnerORM(Model):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)

    name: Mapped[str | None] = mapped_column(String(256))
    owner_type: Mapped[str] = mapped_column(String(32), default="unknown", index=True)

    # Contact info stored as JSON for flexibility
    contact_phone: Mapped[str | None] = mapped_column(String(32))
    contact_telegram: Mapped[str | None] = mapped_column(String(64))
    contact_viber: Mapped[str | None] = mapped_column(String(32))
    contact_whatsapp: Mapped[str | None] = mapped_column(String(32))
    contact_email: Mapped[str | None] = mapped_column(String(128))

    rating: Mapped[float] = mapped_column(Float, default=0.0)
    listing_count: Mapped[int] = mapped_column(Integer, default=0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    listings: Mapped[list["ListingORM"]] = relationship(back_populates="owner")

    __table_args__ = (
        Index("ix_owner_type_rating", "owner_type", "rating"),
        Index("ix_owner_phone", "contact_phone"),
    )


class ListingORM(Model):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="RESTRICT")
    )
    external_id: Mapped[str] = mapped_column(String(128))
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("owners.id", ondelete="SET NULL")
    )

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

    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )

    # Apartment details
    room_count: Mapped[int | None] = mapped_column(Integer)
    area: Mapped[float | None] = mapped_column(Float)
    floor: Mapped[int | None] = mapped_column(Integer)
    total_floors: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    # Owner info from listing (may differ from Owner aggregate)
    owner_name: Mapped[str | None] = mapped_column(String(256))
    owner_type_declared: Mapped[str | None] = mapped_column(String(32))

    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source: Mapped["SourceORM"] = relationship(back_populates="listings")
    owner: Mapped["OwnerORM | None"] = relationship(back_populates="listings")
    photos: Mapped[list["ListingPhotoORM"]] = relationship(
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingPhotoORM.order",
    )
    price_history: Mapped[list["ListingPriceHistoryORM"]] = relationship(
        back_populates="listing", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_listing_src_ext"),
        Index("ix_listing_fingerprint_status", "fingerprint", "status"),
        Index("ix_listing_city_price", "address_city", "price_amount"),
        Index("ix_listing_city_rooms", "address_city", "room_count"),
        Index("ix_listing_status_updated", "status", "updated_at"),
        Index("ix_listing_location", "location", postgresql_using="gist"),
    )


class ListingPhotoORM(Model):
    __tablename__ = "listing_photos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE")
    )
    url: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column(Integer, default=0)

    listing: Mapped["ListingORM"] = relationship(back_populates="photos")


class ListingPriceHistoryORM(Model):
    __tablename__ = "listing_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    listing_id: Mapped[int] = mapped_column(
        ForeignKey("listings.id", ondelete="CASCADE")
    )
    price_amount: Mapped[float] = mapped_column(Float)
    price_currency: Mapped[str] = mapped_column(String(8))
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    listing: Mapped["ListingORM"] = relationship(back_populates="price_history")

    __table_args__ = (
        Index("ix_price_history_listing_date", "listing_id", "recorded_at"),
    )

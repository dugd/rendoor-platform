from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.domain.listing import Listing
from core.domain.listing.value import (
    Money,
    Address,
    Image,
    OwnerInfo,
)
from core.infra.models import ListingORM, SourceORM


class ListingRepository: # TODO: Make mapper
    """SQLAlchemy implementation of listing repository"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, listing: Listing) -> Listing:
        """Save or update a listing"""
        stmt = (
            select(ListingORM)
            .options(joinedload(ListingORM.photos))
            .where(ListingORM.id == listing.uuid)
        )
        result = await self._session.execute(stmt)
        orm_listing = result.unique().scalar_one_or_none()

        if orm_listing:
            # Update existing
            self._update_orm_from_domain(orm_listing, listing)
        else:
            # Create new
            orm_listing = self._create_orm_from_domain(listing)
            self._session.add(orm_listing)

        await self._session.commit()
        await self._session.refresh(orm_listing)

        return self._map_to_domain(orm_listing)

    async def get_by_id(self, listing_id: int) -> Listing | None:
        """Get listing by ID"""
        stmt = (
            select(ListingORM)
            .options(
                joinedload(ListingORM.photos),
                joinedload(ListingORM.source),
            )
            .where(ListingORM.id == listing_id)
        )
        result = await self._session.execute(stmt)
        orm_listing = result.unique().scalar_one_or_none()

        if not orm_listing:
            return None

        return self._map_to_domain(orm_listing)

    async def find_by_fingerprint(self, fingerprint: str) -> list[Listing]:
        """Find listings by fingerprint"""
        stmt = (
            select(ListingORM)
            .options(
                joinedload(ListingORM.photos),
                joinedload(ListingORM.source),
            )
            .where(ListingORM.fingerprint == fingerprint)
        )
        result = await self._session.execute(stmt)
        orm_listings = result.unique().scalars().all()

        return [self._map_to_domain(orm) for orm in orm_listings]

    async def find_by_source_and_external_id(
        self, source_code: str, external_id: str
    ) -> Listing | None:
        """Find listing by source code and external ID"""
        stmt = (
            select(ListingORM)
            .join(ListingORM.source)
            .options(
                joinedload(ListingORM.photos),
                joinedload(ListingORM.source),
            )
            .where(
                SourceORM.code == source_code,
                ListingORM.external_id == external_id,
            )
        )
        result = await self._session.execute(stmt)
        orm_listing = result.unique().scalar_one_or_none()

        if not orm_listing:
            return None

        return self._map_to_domain(orm_listing)

    def _map_to_domain(self, orm: ListingORM) -> Listing:
        """Map ORM model to domain entity"""
        # Map price
        price = None
        if orm.price_amount is not None and orm.price_currency:
            price = Money(amount=orm.price_amount, currency=orm.price_currency)

        # Map address
        address = None
        if orm.address_city and orm.address_country and orm.address_state:
            address = Address(
                country=orm.address_country,
                state=orm.address_state,
                city=orm.address_city,
                district=orm.address_district,
                street=orm.address_street,
                building=orm.address_building,
                zip_code=orm.address_zip,
            )

        # Map location
        location = None
        if orm.location:
            # TODO: implement proper location mapping
            # GeoAlchemy2 returns WKBElement, need to extract coordinates
            # For now, skip location mapping (requires proper geoalchemy2 handling)
            pass

        # Map photos
        photos = []
        if orm.photos:
            photos = [Image(url=photo.url, order=photo.order) for photo in orm.photos]

        # Map owner info
        owner_info = None
        if orm.owner_name or orm.owner_type_declared:
            owner_info = OwnerInfo(
                name=orm.owner_name,
                # owner_type=orm.owner_type_declared or "unknown",
                contact=None,  # Contact info not stored separately in listing
            )

        return Listing(
            uuid=orm.id,
            source_code=orm.source.code,
            external_id=orm.external_id,
            url=orm.url,
            title=orm.title,
            external_owner_id=orm.external_owner_id,
            owner_info=owner_info,
            price=price,
            address=address,
            location=location,
            room_count=orm.room_count,
            area=orm.area,
            floor=orm.floor,
            total_floors=orm.total_floors,
            description=orm.description,
            photos=photos,
            # status=orm.status,
            is_verified=orm.is_verified,
            fingerprint=orm.fingerprint,
            first_seen_at=orm.first_seen_at,
            last_seen_at=orm.last_seen_at,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def _create_orm_from_domain(self, listing: Listing) -> ListingORM:
        """Create new ORM model from domain entity"""
        # This is a simplified version - in production you'd need to handle source_id lookup
        raise NotImplementedError(
            "Creating new listings via repository not yet implemented"
        )

    def _update_orm_from_domain(self, orm: ListingORM, listing: Listing) -> None:
        """Update existing ORM model from domain entity"""
        orm.title = listing.title
        orm.url = listing.url
        orm.fingerprint = listing.fingerprint

        # Update price
        if listing.price:
            orm.price_amount = listing.price.amount
            orm.price_currency = listing.price.currency
        else:
            orm.price_amount = None
            orm.price_currency = None

        # Update address
        if listing.address:
            orm.address_country = listing.address.country
            orm.address_state = listing.address.state
            orm.address_city = listing.address.city
            orm.address_district = listing.address.district
            orm.address_street = listing.address.street
            orm.address_building = listing.address.building
            orm.address_zip = listing.address.zip_code
        else:
            orm.address_country = None
            orm.address_state = None
            orm.address_city = None
            orm.address_district = None
            orm.address_street = None
            orm.address_building = None
            orm.address_zip = None

        # Update apartment details
        orm.room_count = listing.room_count
        orm.area = listing.area
        orm.floor = listing.floor
        orm.total_floors = listing.total_floors
        orm.description = listing.description

        # Update owner info
        if listing.owner_info:
            orm.owner_name = listing.owner_info.name
            orm.owner_type_declared = listing.owner_info.owner_type
        else:
            orm.owner_name = None
            orm.owner_type_declared = None

        # Update status and metadata
        orm.status = listing.status
        orm.is_verified = listing.is_verified
        orm.external_owner_id = listing.external_owner_id

        # Update timestamps
        orm.first_seen_at = listing.first_seen_at
        orm.last_seen_at = listing.last_seen_at
        orm.updated_at = listing.updated_at

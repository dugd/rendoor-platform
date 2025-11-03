"""Mapper for Listing domain entity and ListingORM."""

from typing import Any
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point

from core.domain.listing import Listing
from core.domain.listing import (
    Money,
    Address,
    GeoLocation,
    Image,
    ContactInfo,
    OwnerInfo,
)
from core.infra.models.core import ListingORM


class ListingMapper:
    """Mapper for converting between Listing domain entity and ListingORM."""

    @staticmethod
    def to_domain(orm: ListingORM) -> Listing:
        """
        Convert ListingORM to Listing domain entity.

        Args:
            orm: ORM model instance

        Returns:
            Listing domain entity
        """
        # Parse price
        price = None
        if orm.price_amount is not None and orm.price_currency:
            price = Money(amount=orm.price_amount, currency=orm.price_currency)

        # Parse address
        address = None
        if orm.address_city:
            address = Address(
                country=orm.address_country or "",
                state=orm.address_state or "",
                city=orm.address_city,
                district=orm.address_district,
                street=orm.address_street,
                building=orm.address_building,
                zip_code=orm.address_zip,
            )

        # Parse location
        location = None
        if orm.location is not None:
            geom = to_shape(orm.location)
            location = GeoLocation(latitude=geom.y, longitude=geom.x)

        # Parse owner contacts
        contact = None
        if orm.owner_contacts:
            contact = ContactInfo(
                phone=orm.owner_contacts.get("phone"),
                telegram=orm.owner_contacts.get("telegram"),
                viber=orm.owner_contacts.get("viber"),
                whatsapp=orm.owner_contacts.get("whatsapp"),
                email=orm.owner_contacts.get("email"),
            )

        # Parse owner info
        owner_info = None
        if orm.owner_name or orm.owner_type_declared or contact:
            owner_info = OwnerInfo(
                name=orm.owner_name,
                owner_type=orm.owner_type_declared or "unknown",
                contact=contact,
            )

        # Parse photos
        photos = (
            [Image(url=photo.url, order=photo.order) for photo in orm.photos]
            if orm.photos
            else []
        )

        return Listing(
            uuid=orm.id,
            source_code=orm.source_code,
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
            status=orm.status,
            is_verified=orm.is_verified,
            fingerprint=orm.fingerprint,
            is_archived=orm.is_archived,
            first_seen_at=orm.first_seen_at,
            last_seen_at=orm.last_seen_at,
            created_at=orm.listing_created_at or orm.created_at,
            updated_at=orm.listing_updated_at or orm.updated_at,
        )

    @staticmethod
    def to_orm_dict(listing: Listing) -> dict[str, Any]:
        """
        Convert Listing domain entity to dictionary for ORM insertion.

        Args:
            listing: Domain entity

        Returns:
            Dictionary with ORM-compatible field names and values
        """
        # Prepare location for PostGIS
        location_wkb = None
        if listing.location:
            point = Point(listing.location.longitude, listing.location.latitude)
            location_wkb = from_shape(point, srid=4326)

        # Prepare owner contacts JSON
        owner_contacts = None
        if listing.owner_info and listing.owner_info.contact:
            contact = listing.owner_info.contact
            owner_contacts = {
                k: v
                for k, v in {
                    "phone": contact.phone,
                    "telegram": contact.telegram,
                    "viber": contact.viber,
                    "whatsapp": contact.whatsapp,
                    "email": contact.email,
                }.items()
                if v is not None
            }

        return {
            "id": listing.uuid,
            "source_code": listing.source_code,
            "external_id": listing.external_id,
            "url": listing.url,
            "title": listing.title,
            "fingerprint": listing.fingerprint,
            "price_amount": listing.price.amount if listing.price else None,
            "price_currency": listing.price.currency if listing.price else None,
            "address_country": listing.address.country if listing.address else None,
            "address_state": listing.address.state if listing.address else None,
            "address_city": listing.address.city if listing.address else None,
            "address_district": listing.address.district if listing.address else None,
            "address_street": listing.address.street if listing.address else None,
            "address_building": listing.address.building if listing.address else None,
            "address_zip": listing.address.zip_code if listing.address else None,
            "location": location_wkb,
            "room_count": listing.room_count,
            "area": listing.area,
            "floor": listing.floor,
            "total_floors": listing.total_floors,
            "description": listing.description,
            "external_owner_id": listing.external_owner_id,
            "owner_name": listing.owner_info.name if listing.owner_info else None,
            "owner_type_declared": listing.owner_info.owner_type
            if listing.owner_info
            else None,
            "owner_contacts": owner_contacts,
            "status": listing.status,
            "is_verified": listing.is_verified,
            "is_archived": listing.is_archived,
            "first_seen_at": listing.first_seen_at,
            "last_seen_at": listing.last_seen_at,
            "listing_created_at": listing.created_at,
            "listing_updated_at": listing.updated_at,
        }

    @staticmethod
    def to_orm(listing: Listing, orm: ListingORM | None = None) -> ListingORM:
        """
        Convert Listing domain entity to ListingORM.

        Args:
            listing: Domain entity
            orm: Existing ORM object to update (optional)

        Returns:
            ListingORM instance
        """
        if orm is None:
            orm = ListingORM(
                id=listing.uuid,
                source_code=listing.source_code,
                external_id=listing.external_id,
            )

        # Prepare location for PostGIS
        location_wkb = None
        if listing.location:
            point = Point(listing.location.longitude, listing.location.latitude)
            location_wkb = from_shape(point, srid=4326)

        # Prepare owner contacts JSON
        owner_contacts = None
        if listing.owner_info and listing.owner_info.contact:
            contact = listing.owner_info.contact
            owner_contacts = {
                k: v
                for k, v in {
                    "phone": contact.phone,
                    "telegram": contact.telegram,
                    "viber": contact.viber,
                    "whatsapp": contact.whatsapp,
                    "email": contact.email,
                }.items()
                if v is not None
            }

        # Update all fields
        orm.url = listing.url
        orm.title = listing.title
        orm.fingerprint = listing.fingerprint

        orm.price_amount = listing.price.amount if listing.price else None
        orm.price_currency = listing.price.currency if listing.price else None

        orm.address_country = listing.address.country if listing.address else None
        orm.address_state = listing.address.state if listing.address else None
        orm.address_city = listing.address.city if listing.address else None
        orm.address_district = listing.address.district if listing.address else None
        orm.address_street = listing.address.street if listing.address else None
        orm.address_building = listing.address.building if listing.address else None
        orm.address_zip = listing.address.zip_code if listing.address else None

        orm.location = location_wkb

        orm.room_count = listing.room_count
        orm.area = listing.area
        orm.floor = listing.floor
        orm.total_floors = listing.total_floors
        orm.description = listing.description

        orm.external_owner_id = listing.external_owner_id
        orm.owner_name = listing.owner_info.name if listing.owner_info else None
        orm.owner_type_declared = (
            listing.owner_info.owner_type if listing.owner_info else None
        )
        orm.owner_contacts = owner_contacts

        orm.status = listing.status
        orm.is_verified = listing.is_verified
        orm.is_archived = listing.is_archived

        orm.first_seen_at = listing.first_seen_at
        orm.last_seen_at = listing.last_seen_at
        orm.listing_created_at = listing.created_at
        orm.listing_updated_at = listing.updated_at

        return orm

    @staticmethod
    def photo_to_orm_dict(listing_uuid: Any, photo: Image) -> dict[str, Any]:
        """
        Convert Image to dictionary for ListingPhotoORM insertion.

        Args:
            listing_uuid: UUID of the listing
            photo: Image value object

        Returns:
            Dictionary with ORM-compatible field names and values
        """
        return {
            "listing_id": listing_uuid,
            "url": photo.url,
            "order": photo.order,
        }


__all__ = ["ListingMapper"]

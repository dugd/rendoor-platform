from core.domain.ingest import RawListing
from core.domain.listing import Listing
from core.domain.listing.value import Money, Address, GeoLocation, Image
import hashlib
from typing import Any


class DomRiaNormalizer:
    def __init__(self) -> None:
        self._source_code = "domria"
        self.photo_base_url = "https://cdn.riastatic.com/"
        self.base_domain = "https://dom.ria.com"

    @property
    def source_code(self) -> str:
        """Returns the source code identifier this normalizer handles."""
        return self._source_code

    async def normalize(self, raw: RawListing) -> Listing:
        payload = raw.payload

        external_id = str(payload.get("realty_id", ""))

        url = self._build_url(payload.get("beautiful_url", ""))

        title = self._build_title(payload)

        fingerprint = self._generate_fingerprint(payload)

        # owner_id = str(payload.get("user_id")) if payload.get("user_id") else None
        owner_id = None

        price = self._extract_price(payload)

        address = self._extract_address(payload)

        location = self._extract_location(payload)

        room_count = payload.get("rooms_count")

        area = payload.get("total_square_meters")
        if area is not None:
            area = float(area)

        floor = payload.get("floor")

        description = payload.get("description_uk") or payload.get("description")

        photos = self._extract_photos(payload)

        # NOTE: listing_id=-1 (not yet persisted)
        return Listing(
            listing_id=-1,
            source_code=raw.source_code,
            external_id=external_id,
            url=url,
            title=title,
            fingerprint=fingerprint,
            owner_id=owner_id,
            price=price,
            address=address,
            location=location,
            room_count=room_count,
            area=area,
            floor=floor,
            description=description,
            photos=photos,
        )

    def _build_url(self, beautiful_url: str) -> str:
        """Builds full URL from beautiful_url using base domain"""
        if not beautiful_url:
            return ""
        return f"{self.base_domain}/{beautiful_url}"

    def _build_title(self, payload: dict[str, Any]) -> str:
        """Builds a title for the listing based on available fields."""
        parts = []

        realty_type = payload.get("realty_type_name_uk") or payload.get(
            "realty_type_name"
        )
        if realty_type:
            parts.append(realty_type)

        rooms = payload.get("rooms_count")
        if rooms:
            parts.append(f"{rooms}-кімн.")

        area = payload.get("total_square_meters")
        if area:
            parts.append(f"{area} м²")

        city = payload.get("city_name_uk") or payload.get("city_name")
        if city:
            parts.append(city)

        district = payload.get("district_name_uk") or payload.get("district_name")
        if district:
            parts.append(district)

        return ", ".join(parts) if parts else "Без назви"

    def _generate_fingerprint(self, payload: dict[str, Any]) -> str:
        """Generates a fingerprint for the listing based on key fields."""
        # TODO: Need to verify which fields are best for fingerprinting
        key_fields = [
            str(payload.get("realty_id", "")),
            str(payload.get("location", "")),
            str(payload.get("rooms_count", "")),
            str(payload.get("total_square_meters", "")),
            str(payload.get("floor", "")),
            str(payload.get("price", "")),
        ]

        fingerprint_string = "|".join(key_fields)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def _extract_price(self, payload: dict[str, Any]) -> Money | None:
        """Extracts price information from the payload."""
        price_value = payload.get("price")
        if price_value is None:
            return None

        currency_map = {
            1: "USD",
            2: "EUR",
            3: "UAH",
        }

        currency_id = payload.get("currency_type_id", 3)
        currency = currency_map.get(currency_id, "UAH")

        return Money(amount=float(price_value), currency=currency)

    def _extract_address(self, payload: dict[str, Any]) -> Address | None:
        """Extracts address information from the payload."""
        city = payload.get("city_name_uk") or payload.get("city_name")
        if not city:
            return None

        street = payload.get("street_name_uk") or payload.get("street_name")
        building = payload.get("building_number_str")
        district = payload.get("district_name_uk") or payload.get("district_name")
        state = payload.get("state_name_uk") or payload.get("state_name")

        return Address(
            city=city,
            street=street,
            building=building,
            district=district,
            state=state,
            country="Україна",
            zip_code=None,
        )

    def _extract_location(self, payload: dict[str, Any]) -> GeoLocation | None:
        """Extracts geographical location from the payload."""
        location_str = payload.get("location")
        if not location_str:
            lat = payload.get("latitude")
            lon = payload.get("longitude")
            if lat is not None and lon is not None:
                return GeoLocation(latitude=float(lat), longitude=float(lon))
            return None

        try:
            parts = location_str.split(",")
            if len(parts) == 2:
                latitude = float(parts[0].strip())
                longitude = float(parts[1].strip())
                return GeoLocation(latitude=latitude, longitude=longitude)
        except (ValueError, AttributeError):
            return None

        return None

    def _extract_photos(self, payload: dict[str, Any]) -> list[Image]:
        """Extracts photos from the payload and returns a list of Image objects."""
        photos_dict = payload.get("photos", {})
        if not photos_dict:
            return []

        photos = []
        sorted_photos = sorted(
            photos_dict.values(), key=lambda x: x.get("ordering", 999)
        )

        for photo_data in sorted_photos:
            file_path = photo_data.get("file")
            if file_path:
                url = f"{self.photo_base_url}{file_path}"
                photos.append(
                    Image(
                        url=url,
                        order=photo_data.get("ordering", 0),
                    )
                )

        return photos

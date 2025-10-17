from ..value import Money, Address, GeoLocation, Image


class Listing:
    def __init__(
        self,
        _id: int,
        source_id: str,
        external_id: str,
        owner_id: str,
        url: str,
        title: str,
        fingerprint: str,
        price: Money | None = None,
        address: Address | None = None,
        location: GeoLocation | None = None,
        room_count: int | None = None,
        area: float | None = None,
        floor: int | None = None,
        description: str | None = None,
        photos: list[Image] | None = None,
    ):
        self.id = _id
        self.source_id = source_id
        self.external_id = external_id
        self.owner_id = owner_id
        self.url = url
        self.title = title
        self.fingerprint = fingerprint
        self.price = price
        self.address = address
        self.location = location
        self.room_count = room_count
        self.area = area
        self.floor = floor
        self.description = description
        self.photos = photos or []

    def __repr__(self):
        return f"Listing(id={self.id}, title='{self.title}', price={self.price})"

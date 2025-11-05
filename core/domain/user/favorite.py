from uuid import UUID, uuid4
from datetime import datetime, timezone


class Favorite:
    def __init__(
        self,
        tg_user_id: UUID,
        listing_id: UUID,
        *,
        _uuid: UUID | None = None,
        created_at: datetime | None = None,
    ):
        self._uuid = _uuid or uuid4()
        self._tg_user_id = tg_user_id
        self._listing_id = listing_id
        self._created_at = created_at or datetime.now(timezone.utc)

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def tg_user_id(self) -> UUID:
        return self._tg_user_id

    @property
    def listing_id(self) -> UUID:
        return self._listing_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

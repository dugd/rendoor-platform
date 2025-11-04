from uuid import UUID, uuid4
from datetime import datetime


class Subscription:
    __slots__ = (
        "_uuid",
        "_filter_id",
        "_channel",
        "_chat_id",
        "_is_active",
        "_min_interval_sec",
        "_last_sent_at",
    )

    def __init__(
        self,
        filter_id: UUID,
        chat_id: int,
        *,
        _uuid: UUID | None = None,
        channel: str = "telegram",
        is_active: bool = True,
        min_interval_sec: int = 0,
        last_sent_at: datetime | None = None,
    ):
        self._uuid = _uuid or uuid4()
        self._filter_id = filter_id
        self._channel = channel
        self._chat_id = chat_id
        self._is_active = is_active
        self._min_interval_sec = min_interval_sec
        self._last_sent_at = last_sent_at

    @property
    def id(self) -> UUID:
        return self._uuid

    @property
    def filter_id(self) -> UUID:
        return self._filter_id

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def min_interval_sec(self) -> int:
        return self._min_interval_sec

    @property
    def last_sent_at(self) -> datetime | None:
        return self._last_sent_at

    def activate(self) -> None:
        """Activate this subscription"""
        self._is_active = True

    def deactivate(self) -> None:
        """Deactivate this subscription"""
        self._is_active = False

    def update_last_sent(self, sent_at: datetime) -> None:
        """Update the last sent timestamp"""
        self._last_sent_at = sent_at

    def __repr__(self):
        return (
            f"Subscription(id={self._uuid}, filter_id={self._filter_id}, "
            f"channel={self._channel}, chat_id={self._chat_id}, "
            f"is_active={self._is_active})"
        )

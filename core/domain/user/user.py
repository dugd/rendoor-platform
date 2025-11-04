from uuid import UUID, uuid4
from datetime import datetime


class TgUser:
    __slots__ = (
        "_uuid",
        "_tg_user_id",
        "_tg_chat_id",
        "_username",
        "_first_name",
        "_last_name",
        "_is_premium",
        "_last_interaction",
        "_is_active",
        "_is_admin",
    )

    def __init__(
        self,
        tg_user_id: int,
        tg_chat_id: int,
        *,
        _uuid: UUID | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        is_premium: bool = False,
        last_interaction: datetime | None = None,
        is_active: bool = True,
        is_admin: bool = False,
    ):
        self._uuid = _uuid or uuid4()
        self._tg_user_id = tg_user_id
        self._tg_chat_id = tg_chat_id
        self._username = username
        self._first_name = first_name
        self._last_name = last_name
        self._is_premium = is_premium
        self._last_interaction = last_interaction
        self._is_active = is_active
        self._is_admin = is_admin

    @property
    def uuid(self) -> UUID:
        return self._uuid

    @property
    def tg_user_id(self) -> int:
        return self._tg_user_id

    @property
    def tg_chat_id(self) -> int:
        return self._tg_chat_id

    @property
    def username(self) -> str | None:
        return self._username

    @property
    def first_name(self) -> str | None:
        return self._first_name

    @property
    def last_name(self) -> str | None:
        return self._last_name

    @property
    def is_premium(self) -> bool:
        return self._is_premium

    @property
    def last_interaction(self) -> datetime | None:
        return self._last_interaction

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_admin(self) -> bool:
        return self._is_admin

    def update_last_interaction(self, interaction_time: datetime) -> None:
        self._last_interaction = interaction_time

    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active

    def set_admin(self, is_admin: bool) -> None:
        self._is_admin = is_admin

    def __repr__(self):
        return f"User(id={self.uuid}, tg_user_id={self.tg_user_id}, username={self.username}')"


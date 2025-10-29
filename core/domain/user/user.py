from uuid import UUID, uuid4


class TgUser:
    __slots__ = (
        "_uuid",
        "_tg_user_id",
        "_tg_chat_id",
        "_username",
        "_first_name",
        "_last_name",
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
    ):
        self._uuid = _uuid or uuid4()
        self._tg_user_id = tg_user_id
        self._tg_chat_id = tg_chat_id
        self._username = username
        self._first_name = first_name
        self._last_name = last_name

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

    def __repr__(self):
        return f"User(id={self.uuid}, tg_user_id={self.tg_user_id}, username={self.username}')"


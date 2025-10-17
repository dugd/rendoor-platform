class User:
    __slots__ = ("_id", "_telegram_id", "_username")

    def __init__(
        self,
        _id: int,
        telegram_id: int,
        username: str | None = None,
    ):
        self._id = _id
        self._telegram_id = telegram_id
        self._username = username

    @property
    def id(self) -> int:
        return self._id

    @property
    def telegram_id(self) -> int:
        return self._telegram_id

    @property
    def username(self) -> str | None:
        return self._username

    def __repr__(self):
        return f"User(user_id={self._id}, telegram_id={self._telegram_id}, username={self._username}')"

from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class MessageId:
    """ID of a message"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("MessageId must be positive")


@dataclass(frozen=True, eq=True)
class ChatId:
    """ID of a chat"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("ChatId must be positive")

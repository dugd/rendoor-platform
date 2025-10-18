from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    method: str
    url: str
    params: dict[str, str] | None = None
    data: dict[str, str] | None = None
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class Response:
    status: int
    content: bytes
    headers: dict[str, str]

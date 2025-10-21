from typing import Protocol, Callable

from core.domain.ingest import Request, Response


class HttpPolicy(Protocol):
    async def send(self, req: Request, call_next: Callable) -> Response: ...


class HttpTransport(Protocol):
    async def send(self, req: Request) -> Response: ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, tb): ...


class HttpClient(Protocol):
    async def send(self, req: "Request") -> "Response": ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, tb): ...


__all__ = [
    "HttpPolicy",
    "HttpTransport",
    "HttpClient",
]

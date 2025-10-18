from typing import Protocol, Mapping, Any, Callable

from .types import Request, Response


class Policy(Protocol):
    async def send(self, req: Request, call_next: Callable) -> Response: ...


class AsyncHttpTransport(Protocol):
    async def send(self, req: Request) -> Response: ...


class AsyncClient(Protocol):
    async def send(self, req: "Request") -> "Response": ...


class Provider(Protocol):
    def search(self, filters: Mapping[str, Any]): ...
    def fetch_details(self, ids: list[str]): ...

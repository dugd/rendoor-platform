from typing import Protocol, Callable

from core.domain.client import Request, Response


class HttpPolicy(Protocol):
    async def send(self, req: Request, call_next: Callable) -> Response: ...

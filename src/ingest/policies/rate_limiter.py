import asyncio
import time
from typing import Callable
from ..types import Request, Response


class RateLimiterPolicy:
    def __init__(self, requests_per_second: float):
        self._requests_per_second = requests_per_second
        self._interval = 1 / requests_per_second
        self._last_request_time = 0.0

    async def send(self, req: Request, call_next: Callable) -> Response:
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._interval:
            await asyncio.sleep(self._interval - elapsed)
        self._last_request_time = time.time()
        return await call_next(req)

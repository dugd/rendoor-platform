import asyncio
import time
from typing import Callable

from core.domain.ingest import Request, Response


class RateLimiterPolicy:
    def __init__(self, rps: float, burst: int = 1) -> None:
        self._capacity = burst
        self._tokens = burst
        self._rps = rps
        self._interval = 1 / rps
        self._last_request_time = time.monotonic()
        self.lock = asyncio.Lock()

    async def _refill_tokens(self) -> None:
        current_time = time.monotonic()
        elapsed = current_time - self._last_request_time
        tokens_to_add = int(elapsed * self._rps)
        if tokens_to_add > 0:
            self._tokens = min(self._tokens + tokens_to_add, self._capacity)
            self._last_request_time = current_time

    async def _acquire(self) -> None:
        async with self.lock:
            await self._refill_tokens()
            while self._tokens <= 0:
                await asyncio.sleep(max(self._interval, 0.01))
                await self._refill_tokens()
            self._tokens -= 1

    async def send(self, req: Request, call_next: Callable) -> Response:
        await self._acquire()
        return await call_next(req)

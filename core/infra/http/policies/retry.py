import random
import asyncio
from typing import Callable

from core.domain.ingest import Request, Response


class RetryPolicy:
    def __init__(
        self,
        retry_attempts: int,
        retry_on: tuple[int, ...],
        backoff: tuple[str, float, float] = ("exp_jitter", 0.25, 5.0),
    ):
        self._retry_attempts = retry_attempts
        self._retry_on = set(retry_on)
        self.backoff_type, self.backoff_base, self.backoff_cap = backoff

    def _sleep_duration(self, attempt: int) -> float:
        if self.backoff_type == "fixed":
            return min(self.backoff_base, self.backoff_cap)
        elif self.backoff_type == "linear":
            return min(self.backoff_base * attempt, self.backoff_cap)
        elif self.backoff_type == "exp":
            return min(self.backoff_base * (2 ** (attempt - 1)), self.backoff_cap)
        elif self.backoff_type == "exp_jitter":
            delay = min(self.backoff_base * (2 ** (attempt - 1)), self.backoff_cap)
            return delay * random.uniform(0.5, 1.5)
        else:
            raise ValueError(f"Unknown backoff type: {self.backoff_type}")

    async def send(self, req: Request, call_next: Callable) -> Response:
        last_response: Response | None = None
        for attempt in range(1, self._retry_attempts + 1):
            try:
                resp = await call_next(req)
                if getattr(resp, "status_code", None) not in self._retry_on:
                    return resp
            except Exception:
                if attempt == self._retry_attempts:
                    raise
            if attempt < self._retry_attempts:
                await asyncio.sleep(self._sleep_duration(attempt))
        return last_response

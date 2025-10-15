from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid4())
        start = perf_counter()
        status = 500  # unhandled error by default
        exc: Exception | None = None
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            exc = e
            raise
        finally:
            dur_ms = round((perf_counter() - start) * 1000, 2)
            client = request.client.host if request.client else None
            http_bind = logger.bind(
                type="access",
                request_id=rid,
                method=request.method,
                path=request.url.path,
                query=str(request.url.query),
                status=status,
                duration_ms=dur_ms,
                client_ip=client,
                ua=request.headers.get("user-agent"),
            )

            if exc:
                http_bind.opt(exception=exc).error("Unhandled error")
            else:
                http_bind.info("HTTP request")

        response.headers["X-Request-ID"] = rid
        return response

import aiohttp

from src.ingest.types import Response, Request


class AioHttpTransport:
    def __init__(self, base_url: str, timeout: float = 20) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def send(self, req: Request) -> Response:
        if self._session is None:
            raise RuntimeError(
                "Transport session is not initialized. Use 'async with'."
            )

        async with self._session.request(
            method=req.method,
            url=self._base_url + req.url,
            params=req.params,
            data=req.data,
            headers=req.headers,
            timeout=self._timeout,
        ) as resp:
            content = await resp.read()
            return Response(
                status=resp.status,
                content=content,
                headers=dict(resp.headers),
            )

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()

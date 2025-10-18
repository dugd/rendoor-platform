import aiohttp

from .types import Response, Request


class AioHttpTransport:
    def __init__(self, base_url: str, timeout: float = 20) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._session = aiohttp.ClientSession()

    async def send(self, req: Request) -> Response:
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

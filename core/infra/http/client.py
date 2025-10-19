from core.domain.ingest import Request, Response
from core.ports.ingest import HttpTransport, HttpPolicy


class BaseClient:
    def __init__(
        self,
        transport: HttpTransport,
        policies: list[HttpPolicy],
    ) -> None:
        self._transport = transport
        self._policies = policies

    async def send(self, req: Request) -> Response:
        async def call_chain(i, req: Request) -> Response:
            if i < len(self._policies):
                policy = self._policies[i]
                return await policy.send(req, lambda r: call_chain(i + 1, r))
            else:
                return await self._transport.send(req)

        return await call_chain(0, req)

    async def __aenter__(self):
        await self._transport.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._transport.__aexit__(exc_type, exc, tb)

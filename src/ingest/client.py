from .types import Request, Response
from .interfaces import AsyncHttpTransport, AsyncClient, Policy
from .policies import RateLimiterPolicy


class BaseClient:
    def __init__(
        self,
        transport: "AsyncHttpTransport",
        policies: list[Policy],
    ) -> None:
        self._transport = transport
        self._policies = policies

    async def send(self, req: "Request") -> "Response":
        async def call_chain(i, req: "Request") -> "Response":
            if i < len(self._policies):
                policy = self._policies[i]
                return await policy.send(req, lambda r: call_chain(i + 1, r))
            else:
                return await self._transport.send(req)

        return await call_chain(0, req)


class ClientBuilder:
    def __init__(self) -> None:
        self._policies: list[Policy] = []

    def add_policy(self, policy: Policy) -> "ClientBuilder":
        self._policies.append(policy)
        return self

    async def build(self, transport: "AsyncHttpTransport") -> "AsyncClient":
        return BaseClient(transport, self._policies)


async def build_async_client() -> "AsyncClient":
    from .transport import AioHttpTransport

    transport = AioHttpTransport(base_url="https://example.com")
    builder = ClientBuilder()
    client = await builder.add_policy(RateLimiterPolicy(requests_per_second=5)).build(
        transport
    )
    return client


if __name__ == "__main__":
    import asyncio

    async def main():
        client = await build_async_client()
        request = Request(method="GET", url="/api/data")
        for _ in range(5):
            response = await client.send(request)
            print(f"Response status: {response.status}")
            print(f"Response content: {response.content}")

    asyncio.run(main())

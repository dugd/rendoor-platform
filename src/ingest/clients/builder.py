from src.ingest.interfaces import AsyncClient, Policy, AsyncHttpTransport
from .base import BaseClient


class ClientBuilder:
    def __init__(self) -> None:
        self._policies: list[Policy] = []

    def add_policy(self, policy: Policy) -> "ClientBuilder":
        self._policies.append(policy)
        return self

    async def build(self, transport: "AsyncHttpTransport") -> "AsyncClient":
        return BaseClient(transport, self._policies)


async def build_async_client(base_url: str = "https://example.com") -> "AsyncClient":
    from src.ingest.transports import AioHttpTransport
    from src.ingest.policies import RateLimiterPolicy

    transport = AioHttpTransport(base_url=base_url)
    builder = ClientBuilder()
    client = await builder.add_policy(RateLimiterPolicy(requests_per_second=5)).build(
        transport
    )
    return client


if __name__ == "__main__":
    from src.ingest.types import Request
    import asyncio

    async def main():
        client = await build_async_client()
        request = Request(method="GET", url="/api/data")
        async with client:
            for _ in range(5):
                response = await client.send(request)
                print(f"Response status: {response.status}")
                print(f"Response content: {response.content}")

    asyncio.run(main())

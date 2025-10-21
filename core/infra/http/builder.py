from core.ports.infra import HttpClient, HttpPolicy, HttpTransport
from core.infra.http.client import BaseClient


class ClientBuilder:
    def __init__(self) -> None:
        self._policies: list[HttpPolicy] = []

    def add_policy(self, policy: HttpPolicy) -> "ClientBuilder":
        self._policies.append(policy)
        return self

    async def build(self, transport: HttpTransport) -> HttpClient:
        return BaseClient(transport, self._policies)


async def build_async_client(base_url: str = "https://example.com") -> HttpClient:
    from core.infra.http.transports import AioHttpTransport
    from core.infra.http.policies import RetryPolicy, RateLimiterPolicy

    transport = AioHttpTransport(base_url=base_url)
    builder = ClientBuilder()
    client = (
        await builder.add_policy(RateLimiterPolicy(rps=5))
        .add_policy(RetryPolicy(5, (408, 429, 500, 502, 503, 504)))
        .build(transport)
    )
    return client


if __name__ == "__main__":
    from core.domain.ingest import Request
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

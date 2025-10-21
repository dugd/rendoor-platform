from core.adapters.providers.domria import DomRiaProvider
from core.adapters.normalizers.domria import DomRiaNormalizer


if __name__ == "__main__":
    import asyncio
    from core.infra.http.builder import build_async_client

    async def main():
        client = await build_async_client("https://dom.ria.com")
        provider = DomRiaProvider(client=client)
        normalizer = DomRiaNormalizer()

        page = await provider.search()

        for _ in range(len(page.items) - 2):
            page.items.pop()

        print(page)

        async for listing in provider.fetch([item for item in page.items]):
            print(listing)
            normalized = await normalizer.normalize(listing)
            print(normalized)

    asyncio.run(main())

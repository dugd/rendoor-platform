import json
from typing import Mapping, Any, AsyncIterable

from src.domain.ingest import RawListing
from ..interfaces import AsyncClient
from ..types import Page, Request


class DomRiaProvider:
    DEFAULT_FILTERS = {
        "addMoreRealty": "false",
        "excludeSold": "1",
        "category": "1",
        "realty_type": "2",
        "operation": "3",
        "state_id": "0",
        "city_id": "0",
        "in_radius": "0",
        "with_newbuilds": "0",
        "price_cur": "1",
        "wo_dupl": "1",
        "complex_inspected": "0",
        "sort": "created_at",
        "period": "0",
        "notFirstFloor": "0",
        "notLastFloor": "0",
        "with_map": "0",
        "photos_count_from": "0",
        "with_video_only": "0",
        "firstIteraction": "false",
        "fromAmp": "0",
        "limit": "20",
        "client": "searchV2",
        "type": "list",
        "operation_type": "3",
        "ch": "246_244",
        "mobileStatus": "1",
    }

    def __init__(self, client: AsyncClient, mapper):
        self._client = client
        self._mapper = mapper

    async def search(
        self, filters: Mapping[str, Any] = None, cursor: str | int | None = None
    ) -> Page:
        if cursor is None:
            cursor = 0
        async with self._client:
            resp = await self._client.send(
                Request(
                    "GET",
                    "/node/searchEngine/v2/",
                    params={
                        "page": cursor,
                        **(filters if filters else self.DEFAULT_FILTERS),
                    },
                )
            )
        next_cursor = cursor + 1
        data = json.loads(resp.content)
        items = [str(item) for item in data["items"]]
        return Page(
            items=items, next_cursor=next_cursor, meta={"count": str(data["count"])}
        )

    async def iter(self, ids: list[str]) -> AsyncIterable[RawListing]:
        async with self._client:
            for _id in ids:
                resp = await self._client.send(
                    Request(
                        "GET",
                        f"/realty/data/{_id}",
                        params={
                            "lang_id": "4",
                            "key": "",
                        },
                    )
                )
                data = json.loads(resp.content)
                yield self._mapper.map(data) if self._mapper else data


if __name__ == "__main__":
    import asyncio
    from src.ingest.clients import build_async_client

    async def main():
        client = await build_async_client("https://dom.ria.com")
        provider = DomRiaProvider(client=client, mapper=None)

        page = await provider.search()

        for _ in range(len(page.items) - 2):
            page.items.pop()

        print(page)

        async for listing in provider.iter([item for item in page.items]):
            print(listing)

    asyncio.run(main())

import json
from datetime import datetime
from typing import Mapping, Any, AsyncIterable

from core.domain.ingest import RawListing
from core.domain.client import Page, Request
from core.ports.infra import HttpClient
from core.domain.client import ListingResult


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

    def __init__(
        self,
        client: HttpClient,
        max_listings: int | None = None,
        until_timestamp: int | None = None,
    ) -> None:
        self._client = client
        self._max_listings = max_listings or -1
        self._until_timestamp = until_timestamp
        self._source_code = "domria"
        self._filters = self.DEFAULT_FILTERS

    @property
    def source_code(self) -> str:
        """Returns the source code identifier."""
        return self._source_code

    async def _fetch_search(
        self, filters: Mapping[str, Any], cursor: str | int
    ) -> Page:
        resp = await self._client.send(
            Request(
                "GET",
                "/node/searchEngine/v2/",
                params={
                    "page": cursor,
                    **filters,
                },
            )
        )
        next_cursor = cursor + 1
        data = json.loads(resp.content)
        items = [str(item) for item in data["items"]]
        return Page(
            items=items, next_cursor=next_cursor, meta={"count": str(data["count"])}
        )

    async def _fetch_listing(self, _id: str) -> RawListing:
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
        data = resp.content

        return RawListing(
            source_code=self._source_code,
            external_id=_id,
            payload=json.loads(data),
            fetch_url=resp.url,
            schema_version="1.0",
            fetched_at=datetime.now(),
        )

    async def _fetch_listings(self, ids: list[str]) -> AsyncIterable[RawListing]:
        for _id in ids:
            yield await self._fetch_listing(_id)

    async def _check_until_timestamp(self, listing: RawListing) -> bool:
        created_at = listing.payload.get("publishing_date_ts")
        if created_at and self._until_timestamp:
            return created_at < self._until_timestamp
        return False

    async def fetch(
        self,
        cursor: str | None = None,
    ) -> AsyncIterable[ListingResult]:
        """Fetch listings from the external source."""
        if cursor is None:
            cursor = 0
        async with self._client:
            while True:
                page = await self._fetch_search(self._filters, cursor)

                async for listing in self._fetch_listings(page.items):
                    yield ListingResult(
                        listing=listing,
                        next_cursor=page.next_cursor,
                    )
                    self._max_listings -= 1
                    if self._max_listings == 0:
                        return
                    if await self._check_until_timestamp(listing):
                        return
                if page.next_cursor is None:
                    return
                cursor = page.next_cursor


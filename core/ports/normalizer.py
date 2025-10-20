from typing import Protocol

from core.domain.core import Listing
from core.domain.ingest import RawListing


class Normalizer(Protocol):
    """Normalizer interface for converting RawListing to Listing."""

    async def normalize(self, raw: RawListing) -> Listing: ...


__all__ = [
    "Normalizer",
]

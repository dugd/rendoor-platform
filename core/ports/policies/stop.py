from typing import Protocol

from core.domain.ingest import RawListing


class StopPolicy(Protocol):
    """
    Policy interface to determine when to stop fetching listings.
    """

    def should_stop(self, listing: RawListing) -> bool: ...

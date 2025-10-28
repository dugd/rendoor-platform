from dataclasses import dataclass

from .value import SourceType


@dataclass(frozen=True)
class Source:
    """
    Source of listings.

    Represents a real estate listing source
    """

    code: str
    name: str
    type: SourceType  # website
    is_active: bool = True

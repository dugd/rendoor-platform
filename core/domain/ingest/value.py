from typing import Literal

RawStatus = Literal["processing", "processed", "failed", "skipped"]
SourceType = Literal["website"]

__all__ = [
    "RawStatus",
    "SourceType",
]

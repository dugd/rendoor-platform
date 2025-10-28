from typing import Literal

RawStatus = Literal["processing", "processed", "failed", "skipped"]


__all__ = [
    "RawStatus",
]

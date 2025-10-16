from pydantic import BaseModel


class HealthzResponse(BaseModel):
    status: str


class TimestampResponse(BaseModel):
    timestamp: str


__all__ = [
    "HealthzResponse",
    "TimestampResponse",
]

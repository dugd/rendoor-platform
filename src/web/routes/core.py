from fastapi import APIRouter
from datetime import datetime, timezone

from ..schemas import TimestampResponse, HealthzResponse

router = APIRouter(
    prefix="",
    tags=["diagnostic"],
    responses={404: {"description": "Not found"}},
)


@router.get("/healtz", response_model=HealthzResponse, tags=["diagnostic"])
def healtz():
    return HealthzResponse(status="ok")


@router.get("/timestamp", response_model=TimestampResponse, tags=["diagnostic"])
def timestamp():
    now = datetime.now(timezone.utc).isoformat()
    return TimestampResponse(timestamp=now)


__all__ = [
    "router",
]

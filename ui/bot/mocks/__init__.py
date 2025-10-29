from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4


@dataclass
class MockFilter:
    id: str
    user_id: int
    city: str
    price_min: Optional[int]
    price_max: Optional[int]
    rooms: List[int]
    is_active: bool
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MockUser:
    user_id: int
    first_name: str
    username: Optional[str]
    created_at: datetime = field(default_factory=datetime.now)
    listings_received: int = 0


mock_users: dict[int, MockUser] = {}
mock_filters: dict[str, MockFilter] = {}
mock_favorites: dict[int, List[str]] = {}


def get_or_create_user(
    user_id: int, first_name: str, username: Optional[str] = None
) -> MockUser:
    if user_id not in mock_users:
        mock_users[user_id] = MockUser(
            user_id=user_id, first_name=first_name, username=username
        )
    return mock_users[user_id]


def create_filter(
    user_id: int,
    city: str,
    price_min: Optional[int],
    price_max: Optional[int],
    rooms: List[int],
    is_active: bool = False,
) -> MockFilter:
    filter_id = str(uuid4())

    # Deactivate other filters if the new one is active
    if is_active:
        for filter_obj in mock_filters.values():
            if filter_obj.user_id == user_id:
                filter_obj.is_active = False

    new_filter = MockFilter(
        id=filter_id,
        user_id=user_id,
        city=city,
        price_min=price_min,
        price_max=price_max,
        rooms=rooms,
        is_active=is_active,
    )

    mock_filters[filter_id] = new_filter
    return new_filter


def get_user_filters(user_id: int) -> List[MockFilter]:
    return [f for f in mock_filters.values() if f.user_id == user_id]


def get_active_filter(user_id: int) -> Optional[MockFilter]:
    for filter_obj in mock_filters.values():
        if filter_obj.user_id == user_id and filter_obj.is_active:
            return filter_obj
    return None


def get_user_stats(user_id: int) -> dict:
    user = mock_users.get(user_id)
    filters = get_user_filters(user_id)
    favorites = mock_favorites.get(user_id, [])

    return {
        "filters_count": len(filters),
        "favorites_count": len(favorites),
        "listings_count": user.listings_received if user else 0,
    }


__all__ = [
    "MockUser",
    "MockFilter",
    "get_or_create_user",
    "create_filter",
    "get_user_filters",
    "get_active_filter",
    "get_user_stats",
    "mock_users",
    "mock_filters",
    "mock_favorites",
]

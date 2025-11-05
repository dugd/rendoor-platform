from datetime import datetime, timezone

from core.domain.listing.listing import Listing
from core.domain.user.filter import Filter
from core.domain.notify.subscription import Subscription


def matches_filter(listing: Listing, filter: Filter) -> bool:
    """
    Check if a listing matches filter criteria.

    Args:
        listing: The listing to check
        filter: The filter with search criteria

    Returns:
        True if listing matches all filter criteria, False otherwise
    """
    # City match (required in location_filter)
    if listing.address and filter.location_filter:
        if listing.address.city.lower() != filter.location_filter.city.lower():
            return False
    elif filter.location_filter:
        # Filter has city requirement but listing has no address
        return False

    # Price range (optional filter)
    if filter.price_filter and listing.price:
        if filter.price_filter.price_min is not None:
            if listing.price.amount < filter.price_filter.price_min:
                return False
        if filter.price_filter.price_max is not None:
            if listing.price.amount > filter.price_filter.price_max:
                return False

    # Apartment criteria (optional filter)
    if filter.apartment_filter:
        # Room count
        if filter.apartment_filter.room_count is not None:
            if listing.room_count != filter.apartment_filter.room_count:
                return False

        # Area range
        if filter.apartment_filter.area_min is not None:
            if listing.area is None or listing.area < filter.apartment_filter.area_min:
                return False
        if filter.apartment_filter.area_max is not None:
            if listing.area is None or listing.area > filter.apartment_filter.area_max:
                return False

    return True


def can_send_notification(subscription: Subscription) -> bool:
    """
    Check if notification can be sent based on subscription rate limits.

    Args:
        subscription: The subscription to check

    Returns:
        True if notification can be sent, False if rate limited
    """
    if not subscription.is_active:
        return False

    if subscription.last_sent_at is None:
        return True

    elapsed = (datetime.now(timezone.utc) - subscription.last_sent_at).total_seconds()
    return elapsed >= subscription.min_interval_sec

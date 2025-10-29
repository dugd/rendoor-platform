from typing import Optional, List

from ui.bot.config import ALLOWED_CITIES, MAX_PRICE, MIN_PRICE


def validate_city(text: str) -> Optional[str]:
    text_normalized = text.strip().capitalize()

    if text_normalized in ALLOWED_CITIES:
        return text_normalized

    text_lower = text.lower()
    for city in ALLOWED_CITIES:
        if city.lower() == text_lower:
            return city

    return None


def validate_price(text: str) -> Optional[int]:
    try:
        cleaned = text.strip().replace(" ", "").replace(",", "")
        price = int(cleaned)

        if MIN_PRICE <= price <= MAX_PRICE:
            return price

        return None
    except (ValueError, AttributeError):
        return None


def format_price_range(price_min: Optional[int], price_max: Optional[int]) -> str:
    if price_min and price_max:
        return f"{price_min:,} - {price_max:,} грн".replace(",", " ")
    elif price_min:
        return f"від {price_min:,} грн".replace(",", " ")
    elif price_max:
        return f"до {price_max:,} грн".replace(",", " ")
    else:
        return "без обмежень"


def format_rooms(rooms: List[int]) -> str:
    if len(rooms) == 4:
        return "будь-яка кількість"

    rooms_sorted = sorted(rooms)
    return ", ".join(str(r) for r in rooms_sorted) + "-кімн"

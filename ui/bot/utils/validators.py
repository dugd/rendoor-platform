from typing import Optional

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

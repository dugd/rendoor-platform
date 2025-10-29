from typing import Optional, List


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

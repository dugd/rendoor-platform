from uuid import UUID

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ui.bot.config import ROOMS_OPTIONS


def get_rooms_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for rooms in ROOMS_OPTIONS:
        builder.add(
            InlineKeyboardButton(text=f"{rooms}", callback_data=f"rooms:{rooms}")
        )

    builder.adjust(4)

    builder.row(
        InlineKeyboardButton(text="Будь-яка кількість", callback_data="rooms:all")
    )

    return builder.as_markup()


def get_quick_prices_kb(prices: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for i in range(0, len(prices), 3):
        row_prices = prices[i : i + 3]
        for price in row_prices:
            builder.add(
                InlineKeyboardButton(
                    text=f"{price:,}".replace(
                        ",",
                        " ",
                    ),
                    callback_data=f"price:{price}",
                )
            )
        builder.adjust(len(row_prices))

    return builder.as_markup(resize_keyboard=True)


def get_filter_confirm_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ Активувати і почати пошук", callback_data="filter_confirm:activate"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="💾 Зберегти без активації", callback_data="filter_confirm:save"
        )
    )
    builder.row(
        InlineKeyboardButton(text="❌ Скасувати", callback_data="filter_confirm:cancel")
    )

    return builder.as_markup()


def get_filters_list_kb(filters: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for f in filters:
        builder.row(
            InlineKeyboardButton(text=f.name, callback_data=f"filter_open:{f.id}")
        )
    return builder.as_markup()


def get_filter_card_kb(filter_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Редагувати (не працює)", callback_data=f"filter_edit:{filter_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 Видалити (не працює)", callback_data=f"filter_delete:{filter_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔔 Активувати", callback_data=f"filter_subscribe:{filter_id}"
        )
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="filter_back"))
    return builder.as_markup()


def get_listing_actions_kb(listing_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="⭐ Додати в обране", callback_data=f"fav_add:{listing_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Приховати", callback_data=f"hide:{listing_id}")
    )
    return builder.as_markup()


def get_listing_fav_actions_kb(listing_id: UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="❌ Видалити з обраного", callback_data=f"fav_remove:{listing_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(text="🚫 Приховати", callback_data=f"hide:{listing_id}")
    )
    return builder.as_markup()


def get_favorites_list_kb(
    favorites_with_listings: list[tuple],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    """
    Build favorites list keyboard with pagination.

    Args:
        favorites_with_listings: List of (favorite, listing) tuples
        page: Current page number (1-indexed)
        total_pages: Total number of pages
    """
    builder = InlineKeyboardBuilder()

    # Add listing buttons (one per row for compact list)
    for favorite, listing in favorites_with_listings:
        builder.row(
            InlineKeyboardButton(
                text=f"🏠 {listing.title}",
                callback_data=f"fav_open:{listing.uuid}:{page}",
            )
        )

    # Add pagination controls if multiple pages
    if total_pages > 1:
        pagination_buttons = []

        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"fav_page:{page - 1}")
            )

        # Page indicator (non-clickable, but we can make it clickable with callback that does nothing)
        pagination_buttons.append(
            InlineKeyboardButton(
                text=f"Сторінка {page}/{total_pages}",
                callback_data=f"fav_page_indicator:{page}",
            )
        )

        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(text="Вперед ▶️", callback_data=f"fav_page:{page + 1}")
            )

        builder.row(*pagination_buttons)

    return builder.as_markup()


def get_favorite_detail_kb(listing_id: UUID, page: int) -> InlineKeyboardMarkup:
    """
    Build keyboard for favorite detail view.

    Args:
        listing_id: UUID of the listing
        page: Current page number to return to
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🗑 Видалити з обраного",
            callback_data=f"fav_remove:{listing_id}:{page}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Назад до списку",
            callback_data=f"fav_back:{page}",
        )
    )

    return builder.as_markup()

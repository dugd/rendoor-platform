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

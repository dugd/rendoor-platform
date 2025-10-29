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

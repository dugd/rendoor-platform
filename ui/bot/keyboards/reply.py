from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Створити фільтр"),
        KeyboardButton(text="📋 Мої фільтри"),
    )
    builder.row(
        KeyboardButton(text="❤️ Обране"),
        KeyboardButton(text="📊 Статистика"),
    )
    builder.row(KeyboardButton(text="❓ Довідка"))

    return builder.as_markup(resize_keyboard=True)


def get_subscription_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text="⏸ Зупинити підписку"))
    builder.row(KeyboardButton(text="❤️ Обране"), KeyboardButton(text="📊 Статистика"))

    return builder.as_markup(resize_keyboard=True)


def get_cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Скасувати"))

    return builder.as_markup(resize_keyboard=True)


def get_skip_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="⏭ Пропустити"), KeyboardButton(text="❌ Скасувати")
    )

    return builder.as_markup(resize_keyboard=True)


def get_quick_prices_kb(prices: list[int]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for i in range(0, len(prices), 3):
        row_prices = prices[i : i + 3]
        for price in row_prices:
            builder.add(KeyboardButton(text=f"{price:,}".replace(",", " ")))
        builder.adjust(len(row_prices))

    builder.row(
        KeyboardButton(text="⏭ Пропустити"), KeyboardButton(text="❌ Скасувати")
    )

    return builder.as_markup(resize_keyboard=True)

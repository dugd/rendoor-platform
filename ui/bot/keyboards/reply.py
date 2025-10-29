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

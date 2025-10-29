from aiogram import Router, F
from aiogram.types import Message
from ui.bot.utils.formatters import format_price_range, format_rooms
from ui.bot.mocks import get_user_filters

router = Router(name="filters_manage")


@router.message(F.text == "📋 Мої фільтри")
async def show_filters_list(message: Message):
    filters = get_user_filters(message.from_user.id)

    if not filters:
        await message.answer(
            "У тебе ще немає створених фільтрів.\n\n"
            "Натисни ➕ Створити фільтр, щоб почати!"
        )
        return

    filters_text = "📋 <b>Твої фільтри:</b>\n\n"

    for idx, f in enumerate(filters, 1):
        status = "🟢 Активний" if f.is_active else "⚪️ Неактивний"
        filters_text += f"{idx}. {status}\n"
        filters_text += f"   🏙 {f.city}\n"
        filters_text += f"   💰 {format_price_range(f.price_min, f.price_max)}\n"
        filters_text += f"   🛏 {format_rooms(f.rooms)}\n\n"

    filters_text += "<i>Управління фільтрами буде доступне у наступній версії</i>"

    await message.answer(filters_text)


__all__ = ["router"]

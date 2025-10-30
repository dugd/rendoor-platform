from aiogram import Router, F
from aiogram.types import Message
from ui.bot.utils.formatters import format_price_range, format_rooms
from core.domain.user import TgUser
from core.application.services import FilterService

router = Router(name="filters_manage")


@router.message(F.text == "📋 Мої фільтри")
async def show_filters_list(
    message: Message,
    user: TgUser,
    filter_service: FilterService,
):
    filters = await filter_service.get_user_filters(user.uuid)

    if not filters:
        await message.answer(
            "У тебе ще немає створених фільтрів.\n\n"
            "Натисни ➕ Створити фільтр, щоб почати!"
        )
        return

    filters_text = "📋 <b>Твої фільтри:</b>\n\n"

    for idx, f in enumerate(filters, 1):
        # TODO: Get active status from subscriptions
        status = "⚪️ Неактивний"
        filters_text += f"{idx}. {status}\n"
        filters_text += f"   🏙 {f.location_filter.city}\n"

        # Format price range
        price_min = f.price_filter.price_min if f.price_filter else None
        price_max = f.price_filter.price_max if f.price_filter else None
        filters_text += f"   💰 {format_price_range(price_min, price_max)}\n"

        # Format rooms
        rooms = []
        if f.apartment_filter and f.apartment_filter.room_count:
            rooms = [f.apartment_filter.room_count]
        filters_text += f"   🛏 {format_rooms(rooms)}\n\n"

    filters_text += "<i>Управління фільтрами буде доступне у наступній версії</i>"

    await message.answer(filters_text)


__all__ = ["router"]

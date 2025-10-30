from uuid import UUID

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from core.domain.user import TgUser
from core.application.services import FilterService

from ui.bot.utils.formatters import format_price_range
from ui.bot.states import FiltersManageStates
from ui.bot.keyboards.reply import (
    get_main_menu_kb,
)
from ui.bot.keyboards.inline import (
    get_filters_list_kb,
    get_filter_card_kb,
)

router = Router(name="filters_manage")


@router.message(F.text == "📋 Мої фільтри")
async def show_filters_list(
    message: Message,
    user: TgUser,
    state: FSMContext,
    filter_service: FilterService,
):
    filters = await filter_service.get_user_filters(user.uuid)
    await state.set_state(FiltersManageStates.LIST)

    if not filters:
        await message.answer(
            "У тебе ще немає створених фільтрів.\n\n"
            "Натисни ➕ Створити фільтр, щоб почати!",
            reply_markup=get_main_menu_kb(),
        )
        return

    sent = await message.answer(
        "🔽 Обери фільтр для керування:",
        reply_markup=get_filters_list_kb(filters),
    )

    await state.update_data(current_msg_id=sent.message_id)


@router.callback_query(F.data.startswith("filter_open:"))
async def open_filter_card(
    callback: CallbackQuery,
    filter_service: FilterService,
    state: FSMContext,
):
    fid = UUID(callback.data.split(":")[1])
    f = await filter_service.get_filter_by_id(fid)

    await state.set_state(FiltersManageStates.CARD)

    city = f.location_filter.city if f.location_filter else "—"
    price_min = f.price_filter.price_min if f.price_filter else None
    price_max = f.price_filter.price_max if f.price_filter else None
    rooms = (
        f.apartment_filter.room_count
        if f.apartment_filter and f.apartment_filter.room_count
        else "—"
    )

    text = (
        f"<b>📋 Назва:</b> {f.name}\n"
        f"<b>🏙 Місто:</b> {city}\n"
        f"<b>💰 Ціна:</b> {format_price_range(price_min, price_max)}\n"
        f"<b>🛏 Кімнати:</b> {rooms}\n"
        "<b>Статус:</b> 🔕 Неактивний\n\n"
        "<i>Оберіть дію:</i>"
    )

    data = await state.get_data()
    msg_id = data.get("current_msg_id")

    if msg_id:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=msg_id,
            text=text,
            reply_markup=get_filter_card_kb(fid),
        )
    else:
        await callback.message.edit_text(
            text,
            reply_markup=get_filter_card_kb(fid),
        )


@router.callback_query(F.data == "filter_back")
async def back_to_filters(
    callback: CallbackQuery,
    filter_service: FilterService,
    state: FSMContext,
    user: TgUser,
):
    user_data = await state.get_data()
    msg_id = user_data.get("current_msg_id")

    filters = await filter_service.get_user_filters(user.uuid)
    await state.set_state(FiltersManageStates.LIST)

    if msg_id:
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=msg_id,
            text="🔽 Обери фільтр для керування:",
            reply_markup=get_filters_list_kb(filters),
        )
    else:
        await callback.message.edit_text(
            "🔽 Обери фільтр для керування:",
            reply_markup=get_filters_list_kb(filters),
        )


__all__ = ["router"]

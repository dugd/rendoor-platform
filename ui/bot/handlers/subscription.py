from uuid import UUID
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import get_main_menu_kb, get_subscription_kb
from ui.bot.states import SubscriptionStates
from core.domain.user import TgUser
from core.application.services import FilterService

router = Router(name="subscription")


@router.callback_query(F.data.startswith("filter_subscribe:"))
async def activate_subscription(
        callback: CallbackQuery,
        state: FSMContext,
        user: TgUser,
        filter_service: FilterService,
):
    """
    Handle filter activation from filter card.
    Activates the filter and switches to subscription mode.
    """
    await callback.answer()

    filter_id_str = callback.data.split(":")[1]
    filter_id = UUID(filter_id_str)

    filter_obj = await filter_service.get_filter_by_id(filter_id)

    if not filter_obj:
        await callback.answer("Фільтр не знайдено.", show_alert=True)
        return

    # Activate filter (placeholder - will implement real logic later)
    await filter_service.activate_filter(user.uuid, filter_id)

    await state.set_state(SubscriptionStates.ACTIVE)
    await state.update_data(filter_id=str(filter_id))

    confirmation_message = f"""
<b>Підписка активована!</b>

Фільтр: {filter_obj.name}
Місто: {filter_obj.location_filter.city}

Тепер ви будете отримувати нові оголошення, що відповідають цьому фільтру.
Щоб зупинити підписку, натисніть кнопку «Зупинити підписку».
"""

    await callback.message.answer(
        confirmation_message,
        reply_markup=get_subscription_kb(),
        parse_mode="HTML",
    )


@router.message(F.text == "⏸ Зупинити підписку")
async def stop_subscription(
        message: Message,
        state: FSMContext,
        user: TgUser,
        filter_service: FilterService,
):
    """
    Handle stopping the active subscription.
    Deactivates the filter and returns to main menu.
    """
    data = await state.get_data()
    filter_id_str = data.get("filter_id")

    if not filter_id_str:
        await message.answer(
            "Не знайдено активної підписки.",
            reply_markup=get_main_menu_kb(),
        )
        await state.clear()
        return

    filter_id = UUID(filter_id_str)

    filter_obj = await filter_service.get_filter_by_id(filter_id)

    if filter_obj:
        # Deactivate filter (placeholder - will implement real logic later)
        await filter_service.deactivate_filter(user.uuid, filter_id)

        confirmation_message = f"""
<b>Підписку зупинено</b>

Фільтр: {filter_obj.name}

Ви більше не отримуватимете повідомлення по цьому фільтру.
Щоб знову активувати підписку, перейдіть до керування фільтрами.
"""
    else:
        confirmation_message = """
<b>Підписку зупинено</b>

Ви більше не отримуватимете повідомлення по активних фільтрах.
"""

    await state.clear()

    await message.answer(
        confirmation_message,
        reply_markup=get_main_menu_kb(),
        parse_mode="HTML",
    )


__all__ = ["router"]

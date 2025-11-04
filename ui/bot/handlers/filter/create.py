from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import AiogramError

from ui.bot.keyboards.reply import (
    get_skip_kb,
    get_main_menu_kb,
    get_subscription_kb,
)
from ui.bot.keyboards.inline import (
    get_rooms_kb,
    get_filter_confirm_kb,
    get_quick_prices_kb,
)
from ui.bot.utils import messages, validators
from ui.bot.utils.formatters import format_price_range, format_rooms
from ui.bot.states import FilterCreateStates, SubscriptionStates
from ui.bot.config import (
    QUICK_PRICES,
    ALLOWED_CITIES,
    ROOMS_OPTIONS,
    MIN_PRICE,
    MAX_PRICE,
)
from ui.bot.utils.helpers import (
    display_error,
    edit_flow_message,
    edit_flow_message_from_callback,
)
from core.domain.user import TgUser
from core.application.services import FilterService

router = Router(name="filters_create")


@router.message(F.text == "➕ Створити фільтр")
async def start_filter_creation(message: Message, state: FSMContext):
    await state.set_state(FilterCreateStates.CITY)

    await message.answer(messages.FILTER_CREATION_STARTED, reply_markup=get_skip_kb())

    msg = await message.answer(messages.FILTER_CREATE_CITY)
    await state.update_data(flow_message_id=msg.message_id)


@router.message(FilterCreateStates.CITY, F.text == "⏭ Пропустити")
async def skip_city(message: Message, state: FSMContext):
    await display_error(
        message,
        messages.ERROR_SKIP_NOT_ALLOWED,
    )


@router.message(FilterCreateStates.CITY)
async def process_city(message: Message, state: FSMContext):
    city = validators.validate_city(message.text)

    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    if not city:
        await display_error(
            message,
            messages.ERROR_INVALID_CITY.format(cities=", ".join(ALLOWED_CITIES)),
        )
        return

    await message.delete()
    await state.update_data(city=city)
    await state.set_state(FilterCreateStates.PRICE_MIN)

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=messages.FILTER_CREATE_PRICE_MIN,
        reply_markup=get_quick_prices_kb(QUICK_PRICES[:5]),
        state=state,
    )


@router.message(FilterCreateStates.PRICE_MIN, F.text == "⏭ Пропустити")
async def skip_price_min(message: Message, state: FSMContext):
    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    await message.delete()
    await state.update_data(price_min=None)
    await state.set_state(FilterCreateStates.PRICE_MAX)

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=messages.FILTER_CREATE_PRICE_MAX,
        reply_markup=get_quick_prices_kb(QUICK_PRICES),
        state=state,
    )


@router.callback_query(FilterCreateStates.PRICE_MIN, F.data.startswith("price:"))
async def process_price_min_inline(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    price_data = callback.data.split(":")[1]
    price_min = None if price_data == "skip" else int(price_data)

    await state.update_data(price_min=price_min)
    await state.set_state(FilterCreateStates.PRICE_MAX)

    await edit_flow_message_from_callback(
        message=callback.message,
        text=messages.FILTER_CREATE_PRICE_MAX,
        reply_markup=get_quick_prices_kb(QUICK_PRICES),
        state=state,
    )


@router.message(FilterCreateStates.PRICE_MIN)
async def process_price_min(message: Message, state: FSMContext):
    price_min = validators.validate_price(message.text)

    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    if price_min is None:
        await display_error(
            message,
            messages.ERROR_INVALID_PRICE.format(
                min_price=MIN_PRICE, max_price=MAX_PRICE
            ),
        )
        return

    await message.delete()
    await state.update_data(price_min=price_min)
    await state.set_state(FilterCreateStates.PRICE_MAX)

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=messages.FILTER_CREATE_PRICE_MAX,
        reply_markup=get_quick_prices_kb(QUICK_PRICES),
        state=state,
    )


@router.message(FilterCreateStates.PRICE_MAX, F.text == "⏭ Пропустити")
async def skip_price_max(message: Message, state: FSMContext):
    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    await message.delete()
    await state.update_data(price_max=None)
    await state.set_state(FilterCreateStates.ROOMS)

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=messages.FILTER_CREATE_ROOMS,
        reply_markup=get_rooms_kb(),
        state=state,
    )


@router.callback_query(FilterCreateStates.PRICE_MAX, F.data.startswith("price:"))
async def process_price_max_inline(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    price_data = callback.data.split(":")[1]
    price_max = None if price_data == "skip" else int(price_data)

    # Validate price range
    data = await state.get_data()
    price_min = data.get("price_min")

    if price_min and price_max and price_max < price_min:
        await callback.answer(messages.ERROR_PRICE_RANGE, show_alert=True)
        return

    await state.update_data(price_max=price_max)
    await state.set_state(FilterCreateStates.ROOMS)

    await edit_flow_message_from_callback(
        message=callback.message,
        text=messages.FILTER_CREATE_ROOMS,
        reply_markup=get_rooms_kb(),
        state=state,
    )


@router.message(FilterCreateStates.PRICE_MAX)
async def process_price_max(message: Message, state: FSMContext):
    price_max = validators.validate_price(message.text)

    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    if price_max is None:
        await display_error(
            message,
            messages.ERROR_INVALID_PRICE.format(
                min_price=MIN_PRICE, max_price=MAX_PRICE
            ),
        )
        return

    # Validate price range
    price_min = data.get("price_min")

    if price_min and price_max < price_min:
        await display_error(message, messages.ERROR_PRICE_RANGE)
        return

    await message.delete()
    await state.update_data(price_max=price_max)
    await state.set_state(FilterCreateStates.ROOMS)

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=messages.FILTER_CREATE_ROOMS,
        reply_markup=get_rooms_kb(),
        state=state,
    )


@router.message(FilterCreateStates.ROOMS, F.text == "⏭ Пропустити")
async def skip_room_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    flow_msg_id = data.get("flow_message_id")

    await message.delete()
    await state.update_data(price_max=None)
    await state.set_state(FilterCreateStates.CONFIRM)

    confirmation_text = messages.FILTER_CONFIRM.format(
        city=data["city"],
        price_range=format_price_range(data.get("price_min"), data.get("price_max")),
        rooms=format_rooms(list(ROOMS_OPTIONS)),
    )

    await edit_flow_message(
        bot=message.bot,
        chat_id=message.chat.id,
        flow_msg_id=flow_msg_id,
        text=confirmation_text,
        reply_markup=get_filter_confirm_kb(),
        state=state,
    )


@router.callback_query(FilterCreateStates.ROOMS, F.data == "rooms:skip")
async def skip_rooms_inline(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(rooms=list(ROOMS_OPTIONS))
    await state.set_state(FilterCreateStates.CONFIRM)

    data = await state.get_data()

    confirmation_text = messages.FILTER_CONFIRM.format(
        city=data["city"],
        price_range=format_price_range(data.get("price_min"), data.get("price_max")),
        rooms=format_rooms(list(ROOMS_OPTIONS)),
    )

    await edit_flow_message_from_callback(
        message=callback.message,
        text=confirmation_text,
        reply_markup=get_filter_confirm_kb(),
        state=state,
    )


@router.callback_query(FilterCreateStates.ROOMS, F.data.startswith("rooms:"))
async def process_rooms(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    rooms_data = callback.data.split(":")[1]
    rooms = list(ROOMS_OPTIONS) if rooms_data == "all" else [int(rooms_data)]

    await state.update_data(rooms=rooms)
    await state.set_state(FilterCreateStates.CONFIRM)

    data = await state.get_data()

    confirmation_text = messages.FILTER_CONFIRM.format(
        city=data["city"],
        price_range=format_price_range(data.get("price_min"), data.get("price_max")),
        rooms=format_rooms(rooms),
    )

    await edit_flow_message_from_callback(
        message=callback.message,
        text=confirmation_text,
        reply_markup=get_filter_confirm_kb(),
        state=state,
    )


@router.callback_query(FilterCreateStates.CONFIRM, F.data.startswith("filter_confirm:"))
async def confirm_filter(
    callback: CallbackQuery,
    state: FSMContext,
    user: TgUser,
    filter_service: FilterService,
):
    await callback.answer()

    action = callback.data.split(":")[1]

    if action == "cancel":
        await state.clear()
        await callback.message.edit_text(messages.OPERATION_CANCELLED)
        await callback.message.answer(
            messages.MAIN_MENU_TEXT, reply_markup=get_main_menu_kb()
        )
        return

    data = await state.get_data()
    is_active = action == "activate"

    # Convert rooms list to room_count
    rooms = data.get("rooms", [])
    room_count = rooms[0] if rooms and len(rooms) == 1 else None

    # Generate filter name from city
    filter_name = f"Filter for {data['city']}"

    new_filter = await filter_service.create_filter(
        user_id=user.uuid,
        name=filter_name,
        city=data["city"],
        price_min=data.get("price_min"),
        price_max=data.get("price_max"),
        room_count=room_count,
    )

    try:
        await callback.message.delete()
    except AiogramError:
        pass

    filter_card = f"""
✅ <b>Фільтр створено!</b>

🏙 Місто: {data["city"]}
💰 Ціна: {format_price_range(data.get("price_min"), data.get("price_max"))}
🛏 Кімнати: {format_rooms(data["rooms"])}
"""

    if is_active:
        # Activate the filter (placeholder - will implement real logic later)
        await filter_service.activate_filter(user.uuid, new_filter.id)

        await callback.message.answer(
            filter_card + "\n" + messages.FILTER_CREATED_ACTIVATED,
            reply_markup=get_subscription_kb(),
        )

        await state.set_state(SubscriptionStates.ACTIVE)
        await state.update_data(filter_id=str(new_filter.id))
    else:
        await callback.message.answer(
            filter_card + "\n" + messages.FILTER_CREATED_SAVED,
            reply_markup=get_main_menu_kb(),
            )

        await state.clear()


__all__ = ["router"]

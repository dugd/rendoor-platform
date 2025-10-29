from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import (
    get_cancel_kb,
    get_quick_prices_kb,
    get_main_menu_kb,
    get_subscription_kb,
)
from ui.bot.keyboards.inline import get_rooms_kb, get_filter_confirm_kb
from ui.bot.utils import messages, validators
from ui.bot.utils.validators import format_price_range, format_rooms
from ui.bot.mocks import create_filter, get_user_filters, get_active_filter
from ui.bot.states import FilterCreateStates, SubscriptionStates
from ui.bot.config import QUICK_PRICES, ALLOWED_CITIES

router = Router(name="filters")


@router.message(F.text == "➕ Створити фільтр")
async def start_filter_creation(message: Message, state: FSMContext):
    await state.set_state(FilterCreateStates.CITY)
    await state.update_data(messages_to_delete=[])

    msg = await message.answer(
        messages.FILTER_CREATE_CITY, reply_markup=get_cancel_kb()
    )

    await state.update_data(messages_to_delete=[msg.message_id])


@router.message(FilterCreateStates.CITY)
async def process_city(message: Message, state: FSMContext):
    city = validators.validate_city(message.text)

    if not city:
        error_msg = await message.answer(
            messages.ERROR_INVALID_CITY.format(cities=", ".join(ALLOWED_CITIES))
        )

        # Додаємо повідомлення помилки до списку на видалення
        data = await state.get_data()
        messages_to_delete = data.get("messages_to_delete", [])
        messages_to_delete.extend([message.message_id, error_msg.message_id])
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    # Зберігаємо місто і переходимо до мінімальної ціни
    await state.update_data(city=city)
    await state.set_state(FilterCreateStates.PRICE_MIN)

    msg = await message.answer(
        messages.FILTER_CREATE_PRICE_MIN,
        reply_markup=get_quick_prices_kb(QUICK_PRICES[:5]),  # Перші 5 варіантів
    )

    # Оновлюємо список повідомлень
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.extend([message.message_id, msg.message_id])
    await state.update_data(messages_to_delete=messages_to_delete)


@router.message(FilterCreateStates.PRICE_MIN, F.text == "⏭ Пропустити")
async def skip_price_min(message: Message, state: FSMContext):
    await state.update_data(price_min=None)
    await state.set_state(FilterCreateStates.PRICE_MAX)

    msg = await message.answer(
        messages.FILTER_CREATE_PRICE_MAX, reply_markup=get_quick_prices_kb(QUICK_PRICES)
    )

    # Оновлюємо список повідомлень
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.extend([message.message_id, msg.message_id])
    await state.update_data(messages_to_delete=messages_to_delete)


@router.message(FilterCreateStates.PRICE_MIN)
async def process_price_min(message: Message, state: FSMContext):
    price_min = validators.validate_price(message.text)

    if price_min is None:
        from ui.bot.config import MIN_PRICE, MAX_PRICE

        error_msg = await message.answer(
            messages.ERROR_INVALID_PRICE.format(
                min_price=MIN_PRICE, max_price=MAX_PRICE
            )
        )

        data = await state.get_data()
        messages_to_delete = data.get("messages_to_delete", [])
        messages_to_delete.extend([message.message_id, error_msg.message_id])
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    await state.update_data(price_min=price_min)
    await state.set_state(FilterCreateStates.PRICE_MAX)

    msg = await message.answer(
        messages.FILTER_CREATE_PRICE_MAX, reply_markup=get_quick_prices_kb(QUICK_PRICES)
    )

    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.extend([message.message_id, msg.message_id])
    await state.update_data(messages_to_delete=messages_to_delete)


@router.message(FilterCreateStates.PRICE_MAX, F.text == "⏭ Пропустити")
async def skip_price_max(message: Message, state: FSMContext):
    await state.update_data(price_max=None)
    await state.set_state(FilterCreateStates.ROOMS)

    msg = await message.answer(
        messages.FILTER_CREATE_ROOMS, reply_markup=get_rooms_kb()
    )

    # Оновлюємо список повідомлень
    data = await state.get_data()
    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.extend([message.message_id, msg.message_id])
    await state.update_data(messages_to_delete=messages_to_delete)


@router.message(FilterCreateStates.PRICE_MAX)
async def process_price_max(message: Message, state: FSMContext):
    price_max = validators.validate_price(message.text)

    if price_max is None:
        from config import MIN_PRICE, MAX_PRICE

        error_msg = await message.answer(
            messages.ERROR_INVALID_PRICE.format(
                min_price=MIN_PRICE, max_price=MAX_PRICE
            )
        )

        data = await state.get_data()
        messages_to_delete = data.get("messages_to_delete", [])
        messages_to_delete.extend([message.message_id, error_msg.message_id])
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    # Перевірка діапазону
    data = await state.get_data()
    price_min = data.get("price_min")

    if price_min and price_max < price_min:
        error_msg = await message.answer(messages.ERROR_PRICE_RANGE)

        messages_to_delete = data.get("messages_to_delete", [])
        messages_to_delete.extend([message.message_id, error_msg.message_id])
        await state.update_data(messages_to_delete=messages_to_delete)
        return

    await state.update_data(price_max=price_max)
    await state.set_state(FilterCreateStates.ROOMS)

    msg = await message.answer(
        messages.FILTER_CREATE_ROOMS, reply_markup=get_rooms_kb()
    )

    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.extend([message.message_id, msg.message_id])
    await state.update_data(messages_to_delete=messages_to_delete)


@router.callback_query(FilterCreateStates.ROOMS, F.data.startswith("rooms:"))
async def process_rooms(callback: CallbackQuery, state: FSMContext):
    """
    Обробка вибору кількості кімнат
    """
    await callback.answer()

    rooms_data = callback.data.split(":")[1]

    if rooms_data == "all":
        from config import ROOMS_OPTIONS

        rooms = list(ROOMS_OPTIONS)
    else:
        rooms = [int(rooms_data)]

    await state.update_data(rooms=rooms)
    await state.set_state(FilterCreateStates.CONFIRM)

    # Формуємо підсумок фільтра
    data = await state.get_data()

    confirmation_text = messages.FILTER_CONFIRM.format(
        city=data["city"],
        price_range=format_price_range(data.get("price_min"), data.get("price_max")),
        rooms=format_rooms(rooms),
    )

    # Видаляємо попереднє повідомлення з вибором кімнат
    try:
        await callback.message.delete()
    except:
        pass

    msg = await callback.message.answer(
        confirmation_text, reply_markup=get_filter_confirm_kb()
    )

    messages_to_delete = data.get("messages_to_delete", [])
    messages_to_delete.append(msg.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)


@router.callback_query(FilterCreateStates.CONFIRM, F.data.startswith("filter_confirm:"))
async def confirm_filter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    action = callback.data.split(":")[1]

    if action == "cancel":
        await state.clear()
        await callback.message.edit_text(messages.OPERATION_CANCELLED)
        await callback.message.answer(
            messages.MAIN_MENU_TEXT, reply_markup=get_main_menu_kb()
        )
        return

    # Створюємо фільтр
    data = await state.get_data()
    is_active = action == "activate"

    new_filter = create_filter(
        user_id=callback.from_user.id,
        city=data["city"],
        price_min=data.get("price_min"),
        price_max=data.get("price_max"),
        rooms=data["rooms"],
        is_active=is_active,
    )

    # Видаляємо всі проміжні повідомлення
    messages_to_delete = data.get("messages_to_delete", [])
    for msg_id in messages_to_delete:
        try:
            await callback.bot.delete_message(callback.message.chat.id, msg_id)
        except:
            pass

    # Видаляємо повідомлення з підтвердженням
    try:
        await callback.message.delete()
    except:
        pass

    # Показуємо фінальну картку фільтра
    filter_card = f"""
✅ <b>Фільтр створено!</b>

🏙 Місто: {data["city"]}
💰 Ціна: {format_price_range(data.get("price_min"), data.get("price_max"))}
🛏 Кімнати: {format_rooms(data["rooms"])}
"""

    if is_active:
        await callback.message.answer(
            filter_card + "\n" + messages.FILTER_CREATED_ACTIVATED,
            reply_markup=get_subscription_kb(),
        )

        # Переходимо в режим підписки
        await state.set_state(SubscriptionStates.ACTIVE)
        await state.update_data(filter_id=new_filter.id)
    else:
        await callback.message.answer(
            filter_card + "\n" + messages.FILTER_CREATED_SAVED,
            reply_markup=get_main_menu_kb(),
        )

        await state.clear()


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

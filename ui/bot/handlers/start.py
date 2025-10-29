from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import get_main_menu_kb
from ui.bot.utils import messages
from ui.bot.mocks import get_or_create_user, get_user_stats, get_user_filters

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = get_or_create_user(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        username=message.from_user.username,
    )

    filters = get_user_filters(user.user_id)

    if not filters:
        await message.answer(messages.WELCOME_NEW_USER, reply_markup=get_main_menu_kb())
        return

    stats = get_user_stats(user.user_id)

    await message.answer(
        messages.WELCOME_EXISTING_USER.format(**stats), reply_markup=get_main_menu_kb()
    )


@router.message(F.text == "❌ Скасувати")
async def cancel_operation(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(messages.OPERATION_CANCELLED, reply_markup=get_main_menu_kb())

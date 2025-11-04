from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import get_main_menu_kb
from ui.bot.utils import messages
from core.domain.user import TgUser
from core.services import FilterService

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    user: TgUser,
    filter_service: FilterService,
):
    await state.clear()

    # Get user's filters
    filters = await filter_service.get_user_filters(user.uuid)

    if not filters:
        await message.answer(messages.WELCOME_NEW_USER, reply_markup=get_main_menu_kb())
        return

    # Calculate stats
    stats = {
        "filters_count": len(filters),
        "favorites_count": 0,  # TODO: Implement favorites
        "listings_count": 0,  # TODO: Implement from subscriptions/notifications
    }

    await message.answer(
        messages.WELCOME_EXISTING_USER.format(**stats), reply_markup=get_main_menu_kb()
    )


@router.message(F.text == "❌ Скасувати")
async def cancel_operation(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(messages.OPERATION_CANCELLED, reply_markup=get_main_menu_kb())

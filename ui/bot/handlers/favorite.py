from uuid import UUID

from aiogram import Router, F
from aiogram.types import CallbackQuery

from core.domain.user import TgUser
from core.services import FavoriteService

from ui.bot.keyboards.inline import (
    get_listing_fav_actions_kb,
    get_listing_actions_kb,
)

router = Router(name="favorite")


@router.callback_query(F.data.startswith("fav_add:"))
async def add_listing_to_favorites(
    callback: CallbackQuery,
    favorite_service: FavoriteService,
    user: TgUser,
):
    lid = UUID(callback.data.split(":")[1])

    try:
        await favorite_service.add_to_favorites(user.uuid, lid)
    except ValueError:
        # Listing is already in favorites
        await callback.answer("Оголошення вже в обраних.", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=get_listing_fav_actions_kb(lid),
    )


@router.callback_query(F.data.startswith("fav_remove:"))
async def remove_listing_from_favorites(
    callback: CallbackQuery,
    favorite_service: FavoriteService,
    user: TgUser,
):
    lid = UUID(callback.data.split(":")[1])
    try:
        await favorite_service.remove_from_favorites(user.uuid, lid)
    except ValueError:
        # Listing is not in favorites
        await callback.answer("Оголошення не знайдено в обраних.", show_alert=True)
        return

    await callback.message.edit_reply_markup(
        reply_markup=get_listing_actions_kb(lid),
    )


__all__ = ["router"]

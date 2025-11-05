from uuid import UUID
import math

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from core.domain.user import TgUser
from core.services import FavoriteService
from core.infra.repos import ListingRepository
from core.adapters.formatter.tg_listing_formatter import TelegramListingFormatter

from ui.bot.keyboards.inline import (
    get_listing_fav_actions_kb,
    get_listing_actions_kb,
    get_favorites_list_kb,
    get_favorite_detail_kb,
)
from ui.bot.config import PAGINATION_LIMIT

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
    state: FSMContext,
    favorite_service: FavoriteService,
    listing_repository: ListingRepository,
    user: TgUser,
):
    """Remove listing from favorites and return to list or update keyboard"""
    parts = callback.data.split(":")
    lid = UUID(parts[1])
    page = int(parts[2]) if len(parts) > 2 else None

    try:
        await favorite_service.remove_from_favorites(user.uuid, lid)
    except ValueError:
        # Listing is not in favorites
        await callback.answer("Оголошення не знайдено в обраних.", show_alert=True)
        return

    # If called from favorites list (page is provided), return to list
    if page is not None:
        await callback.answer("Видалено з обраного")
        # Reload favorites list
        await _show_favorites_page(
            callback, state, user, favorite_service, listing_repository, page
        )
    else:
        # Called from a regular listing view, just update keyboard
        await callback.message.edit_reply_markup(
            reply_markup=get_listing_actions_kb(lid),
        )


@router.callback_query(F.data.startswith("fav_open:"))
async def view_favorite_detail(
    callback: CallbackQuery,
    state: FSMContext,
    listing_repository: ListingRepository,
):
    """Show full listing detail when clicked from favorites list"""
    parts = callback.data.split(":")
    listing_id = UUID(parts[1])
    page = int(parts[2])

    # Load listing
    listing = await listing_repository.get_by_id(listing_id)
    if not listing:
        await callback.answer("Оголошення не знайдено", show_alert=True)
        return

    # Format listing
    formatter = TelegramListingFormatter()
    formatted = formatter.format_listing(listing)

    # Build keyboard with back button
    keyboard = get_favorite_detail_kb(listing_id, page)

    # Edit message to show listing detail
    if formatted["photos"]:
        # If has photos, send as media group
        # But we can't edit message to media group, so we'll just show text with link
        # Alternative: delete old message and send new one, but that's not seamless
        # Best approach: show text with first photo or just text
        try:
            # Try to edit with just text
            await callback.message.edit_text(
                formatted["text"],
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=False,
            )
        except Exception:
            # If fails, send as new message
            await callback.message.answer(
                formatted["text"],
                reply_markup=keyboard,
                parse_mode="HTML",
            )
    else:
        # No photos, just show text
        await callback.message.edit_text(
            formatted["text"],
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )

    await callback.answer()


@router.callback_query(F.data.startswith("fav_page:"))
async def change_favorites_page(
    callback: CallbackQuery,
    state: FSMContext,
    user: TgUser,
    favorite_service: FavoriteService,
    listing_repository: ListingRepository,
):
    """Handle pagination button clicks"""
    page = int(callback.data.split(":")[1])

    await _show_favorites_page(
        callback, state, user, favorite_service, listing_repository, page
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fav_back:"))
async def back_to_favorites_list(
    callback: CallbackQuery,
    state: FSMContext,
    user: TgUser,
    favorite_service: FavoriteService,
    listing_repository: ListingRepository,
):
    """Return to favorites list from detail view"""
    page = int(callback.data.split(":")[1])

    await _show_favorites_page(
        callback, state, user, favorite_service, listing_repository, page
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fav_page_indicator:"))
async def page_indicator_click(callback: CallbackQuery):
    """Handle clicks on page indicator (do nothing)"""
    await callback.answer()


async def _show_favorites_page(
    callback: CallbackQuery,
    state: FSMContext,
    user: TgUser,
    favorite_service: FavoriteService,
    listing_repository: ListingRepository,
    page: int,
):
    """Helper function to display a specific page of favorites"""
    # Get total count
    all_favorites = await favorite_service.get_user_favorites(user.uuid, limit=1000, offset=0) # TODO: improve count method
    total_count = len(all_favorites)

    if total_count == 0:
        await callback.message.edit_text(
            "❤️ У тебе поки немає збережених оголошень.\n\n"
            "Коли знайдеш цікавий варіант — додай його в обране!"
        )
        await state.clear()
        return

    # Calculate pagination
    total_pages = math.ceil(total_count / PAGINATION_LIMIT)

    # Clamp page to valid range
    page = max(1, min(page, total_pages))

    offset = (page - 1) * PAGINATION_LIMIT

    # Get favorites for current page
    favorites = await favorite_service.get_user_favorites(
        user.uuid, limit=PAGINATION_LIMIT, offset=offset
    )

    # Load listings for favorites
    favorites_with_listings = []
    for favorite in favorites:
        listing = await listing_repository.get_by_id(favorite.listing_id)
        if listing:
            favorites_with_listings.append((favorite, listing))

    # Build message text
    message_text = f"❤️ <b>Твоє обране ({total_count})</b>\n\n"
    message_text += "<i>Натисни на оголошення, щоб переглянути деталі</i>"

    # Build keyboard
    keyboard = get_favorites_list_kb(favorites_with_listings, page, total_pages)

    # Edit message
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    # Update state
    await state.update_data(current_page=page)


__all__ = ["router"]

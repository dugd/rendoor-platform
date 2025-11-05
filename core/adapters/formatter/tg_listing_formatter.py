from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from core.domain.listing import Listing


class TelegramListingFormatter:
    def format_listing(self, listing: Listing) -> dict:
        text = self._build_text(listing)
        photos = self._build_photos(listing)
        keyboard = self._build_keyboard(listing)

        return {"text": text, "photos": photos, "keyboard": keyboard}

    def format_short(self, listing: Listing) -> str:
        return f"🏠 {listing.title}\n💰 {listing.price.amount} {listing.price.currency}/міс"

    def format_favorite_short(self, listing: Listing, index: int) -> str:
        """Format listing for compact favorites list"""
        price_str = f"{listing.price.amount} {listing.price.currency}/міс" if listing.price else "Ціна не вказана"
        return f"{index}. 🏠 {listing.title} • {price_str}"

    def _build_text(self, listing: Listing) -> str:
        parts = [
            f"<b>{listing.title}</b>",
            "",
            f"💰 <b>{listing.price.amount} {listing.price.currency}/міс</b>",
            f"📍 {listing.address.to_display_string()}",
            f"🏠 {listing.room_count} кімн. • {listing.area} м²",
            f"🏢 {listing.floor} поверх",
            "",
            f"{listing.description[:500]}...",
            "",
            "📱 'unavailable'",
            f"🔗 <a href='{listing.url}'>Переглянути оригінал</a>",
        ]
        return "\n".join(parts)

    def _build_photos(self, listing: Listing) -> List[InputMediaPhoto]:
        if not listing.photos:
            return []

        media = []
        for idx, photo in enumerate(listing.photos[:10]):  # Макс 10 фото
            caption = self._build_text(listing) if idx == 0 else None
            media.append(
                InputMediaPhoto(media=photo.url, caption=caption, parse_mode="HTML")
            )
        return media

    def _build_keyboard(self, listing: Listing) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⭐ Додати в обране",
                        callback_data=f"fav_add:{listing.uuid}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🚫 Приховати", callback_data=f"hide:{listing.uuid}"
                    )
                ],
            ]
        )

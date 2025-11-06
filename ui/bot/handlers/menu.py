from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import math

from ui.bot.keyboards.reply import get_main_menu_kb
from ui.bot.keyboards.inline import (
    get_favorites_list_kb,
    get_stats_navigation_kb,
    get_platform_stats_kb,
)
from ui.bot.utils import messages
from ui.bot.config import PAGINATION_LIMIT
from ui.bot.states import FavoritesStates
from core.domain.user import TgUser
from core.services import FavoriteService, StatisticsService
from core.infra.repos import ListingRepository

router = Router(name="menu")


@router.message(F.text == "📱 Головне меню")
async def show_main_menu(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(messages.MAIN_MENU_TEXT, reply_markup=get_main_menu_kb())


@router.message(F.text == "❓ Довідка")
async def show_help(message: Message):
    help_text = """
📖 <b>Довідка RenDoor</b>

<b>Як користуватись ботом:</b>

1️⃣ <b>Створи фільтр</b>
Вкажи місто, ціну та кількість кімнат. Бот збереже твої параметри.

2️⃣ <b>Активуй фільтр</b>
Активний фільтр автоматично шукає нові оголошення.

3️⃣ <b>Отримуй оголошення</b>
Коли з'являться нові варіанти — ти отримаєш повідомлення.

4️⃣ <b>Зберігай в обране</b>
Цікаві варіанти можна додати в обране для швидкого доступу.

❓ Питання? Пиши @rendoor_support
"""

    await message.answer(help_text)


@router.message(F.text == "📊 Статистика")
async def show_stats(
    message: Message,
    user: TgUser,
    statistics_service: StatisticsService,
):
    """Show user's personal statistics"""
    stats = await statistics_service.get_user_statistics(user.uuid)

    subscription_status = "Так ✅" if stats.active_subscription else "Ні ❌"

    stats_text = f"""
📊 <b>Твоя статистика</b>

📋 Фільтрів створено: {stats.filters_count}
❤️ В обраному: {stats.favorites_count}
🔔 Активна підписка: {subscription_status}

<i>Продовжуй користуватись ботом, щоб знайти ідеальне житло! 🏠</i>
"""

    await message.answer(stats_text, reply_markup=get_stats_navigation_kb())


@router.callback_query(F.data.startswith("stats:platform:"))
async def show_platform_stats(
    callback: CallbackQuery,
    statistics_service: StatisticsService,
):
    """Show platform-wide statistics with period selection"""
    await callback.answer()

    # Extract period
    period = callback.data.split(":")[-1]

    # Map period to days
    period_days_map = {
        "1": 1,
        "7": 7,
        "30": 30,
    }
    period_days = period_days_map.get(period, 7)

    # Platform statistics
    stats = await statistics_service.get_platform_statistics(period_days=period_days)

    # Format period name
    period_name_map = {
        "1": "24 години",
        "7": "тиждень",
        "30": "30 днів",
    }
    period_name = period_name_map.get(period, "тиждень")

    # Format top cities
    if stats.listings_by_city:
        city_stats = "\n".join(
            [
                f"  • {city.city}: {city.count} ({city.avg_price:,.0f} грн)"
                if city.avg_price
                else f"  • {city.city}: {city.count}"
                for city in stats.listings_by_city[:5]
            ]
        )
    else:
        city_stats = "  <i>Немає даних</i>"

    # Format popular search
    if stats.popular_cities:
        popular_cities = "\n".join(
            [
                f"  • {city.city}: {city.count} пошуків"
                for city in stats.popular_cities[:5]
            ]
        )
    else:
        popular_cities = "  <i>Немає даних</i>"

    stats_text = f"""
📈 <b>Статистика платформи</b>
<i>За період: {period_name}</i>

👥 <b>Користувачі:</b>
  • Всього: {stats.total_users}
  • Активних: {stats.active_users}

🏠 <b>Оголошення:</b>
  • Всього: {stats.total_listings}
  • Активних: {stats.active_listings}

🏙 <b>Топ міст (по оголошенням):</b>
{city_stats}

🔍 <b>Популярні міста (по пошукам):</b>
{popular_cities}

📋 <b>Фільтри та підписки:</b>
  • Створено фільтрів: {stats.total_filters}
  • Активних підписок: {stats.active_subscriptions}

❤️ <b>Обране:</b>
  • Всього збережено: {stats.total_favorites}
"""

    # Edit message
    await callback.message.edit_text(
        stats_text, reply_markup=get_platform_stats_kb(period=period)
    )


@router.callback_query(F.data == "stats:user")
async def back_to_user_stats(
    callback: CallbackQuery,
    user: TgUser,
    statistics_service: StatisticsService,
):
    """Return to user's personal statistics"""
    await callback.answer()

    stats = await statistics_service.get_user_statistics(user.uuid)

    subscription_status = "Так ✅" if stats.active_subscription else "Ні ❌"

    stats_text = f"""
📊 <b>Твоя статистика</b>

📋 Фільтрів створено: {stats.filters_count}
❤️ В обраному: {stats.favorites_count}
🔔 Активна підписка: {subscription_status}

<i>Продовжуй користуватись ботом, щоб знайти ідеальне житло! 🏠</i>
"""

    await callback.message.edit_text(stats_text, reply_markup=get_stats_navigation_kb())


@router.message(F.text == "❤️ Обране")
async def show_favorites(
    message: Message,
    state: FSMContext,
    user: TgUser,
    favorite_service: FavoriteService,
    listing_repository: ListingRepository,
):
    """Show user's favorites list with pagination (page 1)"""
    # Get total count first
    all_favorites = await favorite_service.get_user_favorites(
        user.uuid, limit=1000, offset=0
    )  # TODO: improve count method
    total_count = len(all_favorites)

    if total_count == 0:
        await message.answer(
            "❤️ У тебе поки немає збережених оголошень.\n\n"
            "Коли знайдеш цікавий варіант — додай його в обране!"
        )
        return

    # Calculate pagination
    page = 1
    total_pages = math.ceil(total_count / PAGINATION_LIMIT)
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

    # Send message
    sent = await message.answer(message_text, reply_markup=keyboard)

    # Store state
    await state.set_state(FavoritesStates.VIEW)
    await state.update_data(flow_message_id=sent.message_id, current_page=page)

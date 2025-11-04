from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import get_main_menu_kb
from ui.bot.utils import messages
from core.domain.user import TgUser
from core.services import FilterService

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
    filter_service: FilterService,
):
    filters = await filter_service.get_user_filters(user.uuid)

    # TODO: Get favorites count and listings count from database
    stats = {
        "filters_count": len(filters),
        "favorites_count": 0,
        "listings_count": 0,
    }

    stats_text = f"""
📊 <b>Твоя статистика</b>

📋 Фільтрів створено: {stats["filters_count"]}
❤️ В обраному: {stats["favorites_count"]}
📨 Отримано оголошень: {stats["listings_count"]}

<i>Продовжуй користуватись ботом, щоб знайти ідеальне житло! 🏠</i>
"""

    await message.answer(stats_text)


@router.message(F.text == "❤️ Обране")
async def show_favorites(message: Message):
    # TODO: Implement favorites repository and service
    favorites = []

    if not favorites:
        await message.answer(
            "❤️ У тебе поки немає збережених оголошень.\n\n"
            "Коли знайдеш цікавий варіант — додай його в обране!"
        )
        return

    await message.answer(
        f"❤️ <b>Твоє обране</b>\n\n"
        f"Збережено оголошень: {len(favorites)}\n\n"
        f"<i>Повний перегляд обраного буде доступний у наступній версії</i>"
    )

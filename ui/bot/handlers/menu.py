from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ui.bot.keyboards.reply import get_main_menu_kb
from ui.bot.utils import messages

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
async def show_stats(message: Message):
    from ui.bot.mocks import get_user_stats

    stats = get_user_stats(message.from_user.id)

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
    from ui.bot.mocks import mock_favorites

    favorites = mock_favorites.get(message.from_user.id, [])

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

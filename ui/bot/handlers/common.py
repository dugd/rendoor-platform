from aiogram import Router
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start(m):
    await m.answer("Привіт. /filter_new щоб створити фільтр. /help — довідка.")


@router.message(Command("help"))
async def help_(m):
    await m.answer("Команди:\n/filter_new — майстер створення фільтру")


__all__ = [
    "router",
]

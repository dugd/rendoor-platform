from aiogram import Router
from . import start, menu, filter


def get_main_router() -> Router:
    main_router = Router(name="main")

    main_router.include_router(start.router)
    main_router.include_router(filter.get_filter_router())
    main_router.include_router(menu.router)

    return main_router

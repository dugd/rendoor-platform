from aiogram import Router
from . import filter, start, subscription, menu, favorite


def get_main_router() -> Router:
    main_router = Router(name="main")

    main_router.include_router(start.router)
    main_router.include_router(filter.get_filter_router())
    main_router.include_router(subscription.router)
    main_router.include_router(favorite.router)
    main_router.include_router(menu.router)

    return main_router

from aiogram import Router

from . import create, manage


def get_filter_router() -> Router:
    filter_router = Router(name="filter")

    filter_router.include_router(create.router)
    filter_router.include_router(manage.router)

    return filter_router

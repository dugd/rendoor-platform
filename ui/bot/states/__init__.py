from aiogram.fsm.state import State, StatesGroup


class FilterCreateStates(StatesGroup):
    CITY = State()
    PRICE_MIN = State()
    PRICE_MAX = State()
    ROOMS = State()
    CONFIRM = State()


class FilterEditStates(StatesGroup):
    MENU = State()
    CITY = State()
    PRICE_MIN = State()
    PRICE_MAX = State()
    ROOMS = State()


class FiltersManageStates(StatesGroup):
    LIST = State()
    CARD = State()


class SubscriptionStates(StatesGroup):
    ACTIVE = State()


class FavoritesStates(StatesGroup):
    VIEW = State()
    PAGE = State()


__all__ = [
    "FilterCreateStates",
    "FilterEditStates",
    "FiltersManageStates",
    "SubscriptionStates",
    "FavoritesStates",
]

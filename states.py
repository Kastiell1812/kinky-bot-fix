from aiogram.dispatcher.filters.state import State, StatesGroup

class Registration(StatesGroup):
    choosing_language = State()
    entering_city = State()

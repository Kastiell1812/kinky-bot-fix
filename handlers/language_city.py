from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import language_keyboard
from loader import bot

class LanguageCity(StatesGroup):
    choosing_language = State()
    entering_city = State()

@bot.message_handler(commands=['start'], state="*")
async def start_language_choice(message: types.Message, state: FSMContext):
    await state.finish()  # скинути всі стани, щоб не було конфліктів
    await message.answer("Оберіть мову / Выберите язык:", reply_markup=language_keyboard())
    await LanguageCity.choosing_language.set()

@bot.message_handler(state=LanguageCity.choosing_language)
async def language_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in ["українська 🇺🇦", "русский 🇷🇺"]:
        await message.answer("Будь ласка, оберіть мову кнопками.")
        return
    lang = "uk" if "українська" in message.text.lower() else "ru"
    await state.update_data(language=lang)
    await message.answer("Введіть, будь ласка, ваше місто:", reply_markup=types.ReplyKeyboardRemove())
    await LanguageCity.entering_city.set()

@bot.message_handler(state=LanguageCity.entering_city)
async def city_entered(message: types.Message, state: FSMContext):
    city = message.text.strip()
    data = await state.get_data()
    language = data.get("language")
    # Збережи мову та місто в базу (потрібно зробити функцію save_user_language_city)
    from db.database import save_user_language_city
    await save_user_language_city(user_id=message.from_user.id, language=language, city=city)

    if language == "uk":
        await message.answer(f"Дякую! Обрано українську мову, місто: {city}")
        await message.answer("Тепер створимо твою анкету.")
    else:
        await message.answer(f"Спасибо! Выбрали русский язык, город: {city}")
        await message.answer("Теперь создадим твоё анкету.")

    await state.finish()
    # Запусти реєстрацію анкети
    from handlers.registration import cmd_start
    await cmd_start(message)

def register_handlers_language_city(dp: Dispatcher):
    dp.register_message_handler(start_language_choice, commands=["start"], state="*")
    dp.register_message_handler(language_chosen, state=LanguageCity.choosing_language)
    dp.register_message_handler(city_entered, state=LanguageCity.entering_city)

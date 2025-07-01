# handlers/menu.py
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.database import get_user_language
from loader import bot

RULES_UK = (
    "📜 Правила бота:\n\n"
    "1. Заборонено скамити — всі дані будуть передані правоохоронцям.\n"
    "2. Жодної політики.\n"
    "3. Жодних продажів."
)

RULES_RU = (
    "📜 Правила бота:\n\n"
    "1. Запрещено скамить — все данные будут переданы правоохранительным органам.\n"
    "2. Никакой политики.\n"
    "3. Никаких продаж."
)

# Клавіатура головного меню з кнопкою "Правила"
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔍 Перегляд анкет"))
    keyboard.add(KeyboardButton("📜 Правила"))
    # додай інші кнопки меню за потреби
    return keyboard

async def cmd_start(message: types.Message):
    language = await get_user_language(message.from_user.id)
    if language == "uk":
        await message.answer("Ласкаво просимо! Оберіть дію:", reply_markup=get_main_menu())
    else:
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=get_main_menu())

async def cmd_rules(message: types.Message):
    language = await get_user_language(message.from_user.id)
    if language == "uk":
        await message.answer(RULES_UK)
    else:
        await message.answer(RULES_RU)

def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_rules, commands=["rules"])
    dp.register_message_handler(cmd_rules, lambda message: message.text == "📜 Правила")

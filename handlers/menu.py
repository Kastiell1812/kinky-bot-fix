from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from loader import bot

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔍 Перегляд анкет")
    keyboard.add("✏️ Заповнити анкету", "🗑 Видалити анкету")
    return keyboard

async def show_main_menu(chat_id: int):
    await bot.send_message(chat_id, "Вибери дію:", reply_markup=get_main_keyboard())

async def menu_handler(message: types.Message):
    await show_main_menu(message.chat.id)

def register_handlers_menu(dp: Dispatcher):
    dp.register_message_handler(menu_handler, commands=["menu"], state="*")

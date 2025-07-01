from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def language_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    kb.add(KeyboardButton("Українська 🇺🇦"), KeyboardButton("Русский 🇷🇺"))
    return kb

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("📝 Заповнити анкету"))
main_menu.add(KeyboardButton("🗑 Видалити анкету"))
main_menu.add(KeyboardButton("🔍 Перегляд анкет"))

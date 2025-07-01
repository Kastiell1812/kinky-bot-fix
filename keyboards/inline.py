
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_gender_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Чоловік", callback_data="gender_Чоловік"))
    keyboard.add(InlineKeyboardButton("Жінка", callback_data="gender_Жінка"))
    keyboard.add(InlineKeyboardButton("Інше", callback_data="gender_Інше"))
    return keyboard

def get_fetishes_keyboard():
    keyboard = InlineKeyboardMarkup()
    fetishes = ["Без презерватива", "Кремпай", "Зйомка відео", "Публічні місця", "Камшот"]
    for fetish in fetishes:
        keyboard.add(InlineKeyboardButton(fetish, callback_data=f"fetish_{fetish}"))
    keyboard.add(InlineKeyboardButton("Готово", callback_data="fetish_done"))
    return keyboard

def get_looking_for_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("На одну ніч", callback_data="looking_На одну ніч"))
    keyboard.add(InlineKeyboardButton("Постійний секс", callback_data="looking_Постійний секс"))
    return keyboard

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Українська", callback_data="lang_uk"))
    keyboard.add(InlineKeyboardButton("Русский", callback_data="lang_ru"))
    return keyboard

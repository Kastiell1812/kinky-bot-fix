from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from db.database import get_other_users, add_like, check_match
from loader import bot

# Зберігаємо позицію перегляду для кожного користувача
user_profiles = {}

async def show_profile(chat_id: int, user_id: int):
    data = user_profiles.get(user_id)
    if not data:
        users = await get_other_users(user_id)
        if not users:
            await bot.send_message(chat_id, "Немає доступних анкет.")
            return
        user_profiles[user_id] = {"index": 0, "profiles": users}
        data = user_profiles[user_id]

    index = data["index"]
    profiles = data["profiles"]

    if index >= len(profiles):
        await bot.send_message(chat_id, "Це всі анкети, які є на зараз.")
        return

    profile = profiles[index]
    uid, name, age, preferences, photo_id = profile
    text = f"Ім'я: {name}\nВік: {age}\nФетиші: {preferences}"

    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("❤️", callback_data=f"like:{uid}"),
        InlineKeyboardButton("👎", callback_data="dislike")
    )

    await bot.send_photo(chat_id, photo=photo_id, caption=text, reply_markup=keyboard)

async def handle_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = user_profiles.get(user_id)

    if not data:
        await callback.answer("Анкет більше немає.")
        return

    if callback.data.startswith("like:"):
        liked_id = int(callback.data.split(":")[1])
        liked = await add_like(user_id, liked_id)
        if liked:
            if await check_match(user_id, liked_id):
                liked_username = (await bot.get_chat(liked_id)).username
                user_username = (await bot.get_chat(user_id)).username
                if liked_username:
                    await bot.send_message(user_id, f"🎉 У вас взаємний матч! Ось посилання на @{liked_username}")
                else:
                    await bot.send_message(user_id, f"🎉 У вас взаємний матч з користувачем ID {liked_id}!")
                if user_username:
                    await bot.send_message(liked_id, f"🎉 У вас взаємний матч! Ось посилання на @{user_username}")
                else:
                    await bot.send_message(liked_id, f"🎉 У вас взаємний матч з користувачем ID {user_id}!")
        await callback.answer("Ти лайкнув!")
    elif callback.data == "dislike":
        await callback.answer("Пропущено.")

    user_profiles[user_id]["index"] += 1
    await show_profile(callback.message.chat.id, user_id)

async def start_browsing_after_verification(user_id: int):
    await show_profile(user_id, user_id)

async def start_browsing_command(message: types.Message):
    await show_profile(message.chat.id, message.from_user.id)

async def handle_menu_button(message: types.Message):
    if message.text == "🔍 Перегляд анкет":
        await start_browsing_command(message)


def register_handlers_profiles(dp: Dispatcher):
    dp.register_callback_query_handler(handle_callback, lambda c: c.data.startswith("like:") or c.data == "dislike")
    dp.register_message_handler(handle_menu_button, lambda m: m.text == "🔍 Перегляд анкет", state="*")
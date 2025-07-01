from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.database import get_other_users, add_like, check_match, get_user_language
from loader import bot

user_profiles = {}

async def show_profile(chat_id: int, user_id: int):
    data = user_profiles.get(user_id)
    if not data:
        users = await get_other_users(user_id)
        if not users:
            language = await get_user_language(user_id)
            msg = "Немає доступних анкет." if language == "uk" else "Нет доступных анкет."
            await bot.send_message(chat_id, msg)
            return
        user_profiles[user_id] = {"index": 0, "profiles": users}
        data = user_profiles[user_id]

    index = data["index"]
    profiles = data["profiles"]

    if index >= len(profiles):
        language = await get_user_language(user_id)
        msg = "Це всі анкети, які є на зараз." if language == "uk" else "Это все анкеты на данный момент."
        await bot.send_message(chat_id, msg)
        return

    profile = profiles[index]
    uid, name, age, city, preferences, photo_id = profile
    language = await get_user_language(user_id)
    if language == "uk":
        text = f"Ім'я: {name}\nВік: {age}\nМісто: {city}\nФетиші: {preferences}"
    else:
        text = f"Имя: {name}\nВозраст: {age}\nГород: {city}\nФетиши: {preferences}"

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
        language = await get_user_language(user_id)
        msg = "Анкет більше немає." if language == "uk" else "Анкет больше нет."
        await callback.answer(msg)
        return

    if callback.data.startswith("like:"):
        liked_id = int(callback.data.split(":")[1])
        await add_like(user_id, liked_id)
        is_match = await check_match(user_id, liked_id)
        language = await get_user_language(user_id)

        if is_match:
            liked_username = (await bot.get_chat(liked_id)).username or liked_id
            user_username = (await bot.get_chat(user_id)).username

            if language == "uk":
                await bot.send_message(user_id, f"🎉 У вас взаємний матч! Ось посилання на @{liked_username}")
                if user_username:
                    await bot.send_message(liked_id, f"🎉 У вас взаємний матч! Ось посилання на @{user_username}")
                else:
                    await bot.send_message(liked_id, f"🎉 У вас взаємний матч з користувачем ID {user_id}!")
            else:
                await bot.send_message(user_id, f"🎉 У вас взаимный матч! Вот ссылка на @{liked_username}")
                if user_username:
                    await bot.send_message(liked_id, f"🎉 У вас взаимный матч! Вот ссылка на @{user_username}")
                else:
                    await bot.send_message(liked_id, f"🎉 У вас взаимный матч с пользователем ID {user_id}!")

        await callback.answer("Ти лайкнув!" if language == "uk" else "Ты лайкнул!")

    elif callback.data == "dislike":
        language = await get_user_language(user_id)
        await callback.answer("Пропущено." if language == "uk" else "Пропущено.")

    # Переходимо до наступного профілю
    user_profiles[user_id]["index"] += 1
    await show_profile(callback.message.chat.id, user_id)

async def cmd_start_view_profiles(message: types.Message):
    await show_profile(message.chat.id, message.from_user.id)

# Ось нова функція, щоб уникнути ImportError
async def start_browsing_after_verification(user_id: int):
    # Просто починаємо показувати анкети користувачу
    await show_profile(user_id, user_id)

def register_handlers_profiles(dp: Dispatcher):
    dp.register_message_handler(cmd_start_view_profiles, lambda message: message.text == "🔍 Перегляд анкет")
    dp.register_callback_query_handler(handle_callback, lambda c: c.data.startswith(("like:", "dislike")))

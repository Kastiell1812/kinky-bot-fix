from aiogram import types, Dispatcher
from loader import bot
from handlers.menu import show_main_menu

async def process_verify(callback: types.CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup()  # Прибрати кнопки
    await bot.send_message(callback.from_user.id, "Анкету верифіковано.")
    await bot.send_message(user_id, "✅ Твою анкету підтверджено! Тепер ти можеш переглядати інших користувачів.")
    await show_main_menu(user_id, bot)  # Відправляємо кнопки
    from handlers.profiles import start_browsing_after_verification
    await start_browsing_after_verification(user_id)

async def process_reject(callback: types.CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup()
    await bot.send_message(user_id, "❌ Твою анкету відхилено. Спробуй ще раз.")

async def process_repeat_video(callback: types.CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    await callback.message.edit_reply_markup()
    await bot.send_message(user_id, "🔄 Адмін просить надіслати нове відео для верифікації. Надішли відео у відповідь.")

def register_handlers_admin(dp: Dispatcher):
    dp.register_callback_query_handler(process_verify, lambda c: c.data.startswith("verify:"))
    dp.register_callback_query_handler(process_reject, lambda c: c.data.startswith("reject:"))
    dp.register_callback_query_handler(process_repeat_video, lambda c: c.data.startswith("repeat_video:"))

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from db.database import add_user_with_photo
from config import ADMIN_CHAT_ID
from loader import bot

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_preferences = State()
    waiting_for_photo = State()
    waiting_for_phone = State()
    waiting_for_video = State()

async def cmd_start(message: types.Message):
    await message.answer("Привіт! Давай створимо твою анкету. Як тебе звати?")
    await Registration.waiting_for_name.set()

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Скільки тобі років?")
    await Registration.waiting_for_age.set()

async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Будь ласка, введи свій вік цифрами.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Опиши свої вподобання (хештеги, фетиші тощо).")
    await Registration.waiting_for_preferences.set()

async def process_preferences(message: types.Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    await message.answer("Надішли своє фото профілю.")
    await Registration.waiting_for_photo.set()

async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        await message.answer("Будь ласка, надішли фотографію.")
        return
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📞 Надіслати мій номер", request_contact=True))
    keyboard.add("Пропустити")

    await message.answer("Надішли свій номер телефону або пропусти цей крок.", reply_markup=keyboard)
    await Registration.waiting_for_phone.set()

async def process_phone(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text == "Пропустити":
        phone = None
    else:
        await message.answer("Будь ласка, натисни кнопку, щоб надіслати номер, або пропусти.")
        return

    await state.update_data(phone=phone)
    await message.answer("Тепер надішли відео для верифікації (можна пропустити).", reply_markup=ReplyKeyboardRemove())
    await Registration.waiting_for_video.set()

async def process_video(message: types.Message, state: FSMContext):
    if message.content_type in [ContentType.VIDEO, ContentType.VIDEO_NOTE]:
        video_id = message.video.file_id if message.content_type == ContentType.VIDEO else message.video_note.file_id
        await state.update_data(video_id=video_id)
    else:
        await message.answer("Будь ласка, надішли відео або пропусти командою /skipvideo.")
        return

    await save_and_send_to_admin(message, state)

async def skip_video(message: types.Message, state: FSMContext):
    await save_and_send_to_admin(message, state)

async def save_and_send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user_with_photo(
        user_id=message.from_user.id,
        name=data['name'],
        age=data['age'],
        preferences=data['preferences'],
        photo_id=data['photo_id'],
        phone=data.get('phone')
    )

    username = message.from_user.username or "(немає username)"
    caption = (
        f"Нова анкета для верифікації:\n"
        f"Ім'я: {data['name']}\n"
        f"Вік: {data['age']}\n"
        f"Вподобання: {data['preferences']}\n"
        f"Телефон: {data.get('phone', 'Не надано')}\n"
        f"Username: @{username}"
    )

    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("✅ Верифікувати", callback_data=f"verify:{message.from_user.id}"),
        InlineKeyboardButton("❌ Відхилити", callback_data=f"reject:{message.from_user.id}"),
        InlineKeyboardButton("🔄 Запитати повторне відео", callback_data=f"repeat_video:{message.from_user.id}")
    )

    await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=data['photo_id'], caption=caption, reply_markup=keyboard)
    if 'video_id' in data:
        await bot.send_video(chat_id=ADMIN_CHAT_ID, video=data['video_id'], caption=f"Відео користувача {data['name']}")

    await message.answer("Анкета надіслана на перевірку адміну. Очікуй підтвердження.")
    await state.finish()

def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    dp.register_message_handler(process_name, state=Registration.waiting_for_name)
    dp.register_message_handler(process_age, state=Registration.waiting_for_age)
    dp.register_message_handler(process_preferences, state=Registration.waiting_for_preferences)
    dp.register_message_handler(process_photo, content_types=types.ContentType.PHOTO, state=Registration.waiting_for_photo)
    dp.register_message_handler(process_phone, content_types=[types.ContentType.CONTACT, types.ContentType.TEXT], state=Registration.waiting_for_phone)
    dp.register_message_handler(process_video, content_types=[ContentType.VIDEO, ContentType.VIDEO_NOTE], state=Registration.waiting_for_video)
    dp.register_message_handler(skip_video, commands=["skipvideo"], state=Registration.waiting_for_video)

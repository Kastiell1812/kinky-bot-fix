from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from db.database import add_user_with_photo
from config import ADMIN_CHAT_ID
from loader import bot

class Registration(StatesGroup):
    waiting_for_language = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_preferences = State()
    waiting_for_photo = State()
    waiting_for_phone = State()
    waiting_for_video = State()

async def cmd_start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("Українська 🇺🇦", "Русский 🇷🇺")
    await message.answer("Оберіть мову / Выберите язык:", reply_markup=keyboard)
    await Registration.waiting_for_language.set()

async def process_language(message: types.Message, state: FSMContext):
    language = message.text
    if language not in ["Українська 🇺🇦", "Русский 🇷🇺"]:
        await message.answer("Будь ласка, оберіть одну з запропонованих мов.")
        return
    lang_code = "uk" if "Українська" in language else "ru"
    await state.update_data(language=lang_code)
    if lang_code == "uk":
        await message.answer("Як тебе звати?", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    await Registration.waiting_for_name.set()

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("Скільки тобі років?")
    else:
        await message.answer("Сколько тебе лет?")
    await Registration.waiting_for_age.set()

async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        data = await state.get_data()
        lang = data.get('language', 'uk')
        if lang == "uk":
            await message.answer("Будь ласка, введи свій вік цифрами.")
        else:
            await message.answer("Пожалуйста, введи свой возраст цифрами.")
        return
    await state.update_data(age=int(message.text))
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("З якого ти міста?")
    else:
        await message.answer("Из какого ты города?")
    await Registration.waiting_for_city.set()

async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    if not city:
        data = await state.get_data()
        lang = data.get('language', 'uk')
        if lang == "uk":
            await message.answer("Будь ласка, введи назву міста.")
        else:
            await message.answer("Пожалуйста, введи название города.")
        return
    await state.update_data(city=city)
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("Опиши свої вподобання (хештеги, фетиші тощо).")
    else:
        await message.answer("Опиши свои предпочтения (хештеги, фетиши и т.д.).")
    await Registration.waiting_for_preferences.set()

async def process_preferences(message: types.Message, state: FSMContext):
    await state.update_data(preferences=message.text)
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("Надішли своє фото профілю.")
    else:
        await message.answer("Отправь свое фото профиля.")
    await Registration.waiting_for_photo.set()

async def process_photo(message: types.Message, state: FSMContext):
    if not message.photo:
        data = await state.get_data()
        lang = data.get('language', 'uk')
        if lang == "uk":
            await message.answer("Будь ласка, надішли фотографію.")
        else:
            await message.answer("Пожалуйста, отправь фотографию.")
        return
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📞 Надіслати мій номер", request_contact=True))
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("Надішли свій номер телефону.", reply_markup=keyboard)
    else:
        await message.answer("Отправь свой номер телефона.", reply_markup=keyboard)
    await Registration.waiting_for_phone.set()

async def process_phone(message: types.Message, state: FSMContext):
    if not message.contact:
        data = await state.get_data()
        lang = data.get('language', 'uk')
        if lang == "uk":
            await message.answer("Будь ласка, натисни кнопку, щоб надіслати номер.")
        else:
            await message.answer("Пожалуйста, нажми кнопку, чтобы отправить номер.")
        return
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    lang = data.get('language', 'uk')
    if lang == "uk":
        await message.answer("Тепер надішли коротке відео з фразою 'Привіт Кінкі' для верифікації.")
    else:
        await message.answer("Теперь отправь короткое видео с фразой 'Привет Кинки' для верификации.")
    await Registration.waiting_for_video.set()

async def process_video(message: types.Message, state: FSMContext):
    if message.content_type not in [ContentType.VIDEO, ContentType.VIDEO_NOTE]:
        data = await state.get_data()
        lang = data.get('language', 'uk')
        if lang == "uk":
            await message.answer("Будь ласка, надішли відео повідомлення.")
        else:
            await message.answer("Пожалуйста, отправь видео сообщение.")
        return
    video_id = message.video.file_id if message.content_type == ContentType.VIDEO else message.video_note.file_id
    await state.update_data(video_id=video_id)

    await save_and_send_to_admin(message, state)

async def save_and_send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await add_user_with_photo(
            user_id=message.from_user.id,
            name=data['name'],
            age=data['age'],
            city=data.get('city', ''),
            preferences=data['preferences'],
            photo_id=data['photo_id'],
            phone=data.get('phone'),
            language=data.get('language', 'uk')
        )
    except Exception as e:
        await message.answer("Сталася помилка при відправці анкети адміну.")
        import logging
        logging.error(f"Помилка при збереженні користувача в базу: {e}")
        await state.finish()
        return

    username = message.from_user.username or "(немає username)"
    lang = data.get('language', 'uk')

    caption = (
        f"Нова анкета для верифікації:\n"
        f"Мова: {lang}\n"
        f"Ім'я: {data['name']}\n"
        f"Вік: {data['age']}\n"
        f"Місто: {data.get('city', '')}\n"
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

    try:
        await bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=data['photo_id'], caption=caption, reply_markup=keyboard)
        if 'video_id' in data:
            await bot.send_video(chat_id=ADMIN_CHAT_ID, video=data['video_id'], caption=f"Відео користувача {data['name']}")
    except Exception as e:
        await message.answer("Помилка при відправці адміну.")
        import logging
        logging.error(f"Помилка при відправці адміну: {e}")
        await state.finish()
        return

    if lang == "uk":
        await message.answer("Анкета надіслана на перевірку адміну. Очікуй підтвердження.")
    else:
        await message.answer("Анкета отправлена на проверку администратору. Ожидай подтверждения.")
    await state.finish()

def register_handlers_registration(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"], state="*")
    dp.register_message_handler(process_language, state=Registration.waiting_for_language)
    dp.register_message_handler(process_name, state=Registration.waiting_for_name)
    dp.register_message_handler(process_age, state=Registration.waiting_for_age)
    dp.register_message_handler(process_city, state=Registration.waiting_for_city)
    dp.register_message_handler(process_preferences, state=Registration.waiting_for_preferences)
    dp.register_message_handler(process_photo, content_types=types.ContentType.PHOTO, state=Registration.waiting_for_photo)
    dp.register_message_handler(process_phone, content_types=[types.ContentType.CONTACT], state=Registration.waiting_for_phone)
    dp.register_message_handler(process_video, content_types=[ContentType.VIDEO, ContentType.VIDEO_NOTE], state=Registration.waiting_for_video)

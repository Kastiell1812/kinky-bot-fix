# main.py
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from config import BOT_TOKEN
from db.database import init_db
from handlers.registration import register_handlers_registration
from handlers.profiles import register_handlers_profiles
from handlers.admin import register_handlers_admin
from handlers.menu import register_handlers_menu

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_handlers_registration(dp)
register_handlers_profiles(dp)
register_handlers_admin(dp)
register_handlers_menu(dp)

async def on_startup(dp):
    await bot.delete_webhook()
    await init_db()
    logging.info("Bot started!")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)

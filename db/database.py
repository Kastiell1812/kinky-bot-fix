import aiosqlite
from datetime import datetime
from aiogram import types

DB_PATH = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                city TEXT,
                preferences TEXT,
                photo_id TEXT,
                phone TEXT,
                language TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                liker_id INTEGER,
                liked_id INTEGER,
                UNIQUE(liker_id, liked_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                report_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_user_with_photo(user_id: int, name: str, age: int, city: str, preferences: str, photo_id: str, phone: str = None, language: str = "uk"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, name, age, city, preferences, photo_id, phone, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, age, city, preferences, photo_id, phone, language))
        await db.commit()

async def get_other_users(exclude_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, name, age, city, preferences, photo_id FROM users WHERE user_id != ?
        """, (exclude_user_id,))
        rows = await cursor.fetchall()
        return rows

async def add_like(liker_id: int, liked_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute("""
                INSERT INTO likes (liker_id, liked_id) VALUES (?, ?)
            """, (liker_id, liked_id))
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

async def check_match(user1_id: int, user2_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT 1 FROM likes WHERE liker_id = ? AND liked_id = ?
        """, (user2_id, user1_id))
        row = await cursor.fetchone()
        return row is not None

async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await db.commit()

async def cmd_delete_profile(message: types.Message):
    user_id = message.from_user.id
    await delete_user(user_id)
    await message.answer("Твою анкету видалено.")

async def get_user_language(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else "uk"

async def save_report(reporter_id: int, target_user_id: int, report_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO reports (reporter_id, target_user_id, report_text, created_at)
            VALUES (?, ?, ?, ?)
        """, (reporter_id, target_user_id, report_text, datetime.utcnow().isoformat()))
        await db.commit()

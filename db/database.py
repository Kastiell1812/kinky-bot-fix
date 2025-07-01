import aiosqlite

DB_PATH = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                preferences TEXT,
                photo_id TEXT,
                phone TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                liker_id INTEGER,
                liked_id INTEGER,
                UNIQUE(liker_id, liked_id)
            )
        """)
        await db.commit()

async def add_user_with_photo(user_id: int, name: str, age: int, preferences: str, photo_id: str, phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, name, age, preferences, photo_id, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, age, preferences, photo_id, phone))
        await db.commit()

async def get_other_users(exclude_user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, name, age, preferences, photo_id FROM users WHERE user_id != ?
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

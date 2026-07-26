import aiosqlite
import datetime
from utils.logger import logger

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    normalized_link TEXT UNIQUE,
                    date_posted TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER,
                    chat_id INTEGER,
                    username TEXT,
                    last_link_date TIMESTAMP,
                    total_links INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, chat_id)
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_link ON links(normalized_link)")
            await db.commit()
            logger.info("Database initialized successfully.")

    async def link_exists(self, link: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM links WHERE normalized_link = ?", (link,)) as cursor:
                return await cursor.fetchone() is not None

    async def store_link(self, link: str):
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("INSERT INTO links (normalized_link, date_posted) VALUES (?, ?)", 
                                 (link, datetime.datetime.now(datetime.timezone.utc)))
                await db.commit()
            except aiosqlite.IntegrityError:
                pass # Already exists

    async def update_user_activity(self, user_id: int, chat_id: int, username: str):
        now = datetime.datetime.now(datetime.timezone.utc)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO users (user_id, chat_id, username, last_link_date, total_links)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(user_id, chat_id) DO UPDATE SET
                    last_link_date = excluded.last_link_date,
                    username = excluded.username,
                    total_links = total_links + 1
            """, (user_id, chat_id, username, now))
            await db.commit()

    async def get_inactive_users(self) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id, chat_id, username, last_link_date FROM users") as cursor:
                return await cursor.fetchall()

    async def remove_user(self, user_id: int, chat_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
            await db.commit()

db = DatabaseManager("bot_database.db")

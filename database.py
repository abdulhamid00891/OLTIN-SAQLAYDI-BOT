import aiosqlite
import os
from config import DATABASE_PATH

async def init_db():
    """Database yaratish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Playlist jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS playlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                file_type TEXT DEFAULT 'video',
                title TEXT,
                url TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        await db.commit()

async def add_user(user_id: int, username: str = None, first_name: str = None):
    """Yangi foydalanuvchi qo'shish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        await db.commit()

async def add_to_playlist(user_id: int, file_id: str, file_type: str, title: str, url: str):
    """Playlistga video qo'shish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO playlist (user_id, file_id, file_type, title, url)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, file_id, file_type, title, url))
        await db.commit()

async def get_playlist(user_id: int):
    """Foydalanuvchi playlistini olish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM playlist WHERE user_id = ? ORDER BY added_at DESC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def remove_from_playlist(playlist_id: int, user_id: int):
    """Playlistdan o'chirish"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            DELETE FROM playlist WHERE id = ? AND user_id = ?
        """, (playlist_id, user_id))
        await db.commit()

async def get_user_count():
    """Umumiy foydalanuvchilar soni"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

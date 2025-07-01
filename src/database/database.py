"""Database management for the Epic Games Discord Bot."""

import aiosqlite
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize the database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    notification_channel_id INTEGER,
                    notification_time TEXT DEFAULT '13:00',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS notified_games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    guild_id INTEGER NOT NULL,
                    notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(game_id, guild_id)
                )
            """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT NOT NULL,
                    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_message TEXT
                )
            """
            )

            await db.commit()
            logger.info("Database initialized successfully")

    async def get_guild_settings(self, guild_id: int) -> Optional[Tuple[int, str]]:
        """Get guild notification settings."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT notification_channel_id, notification_time FROM guild_settings WHERE guild_id = ?",
                (guild_id,),
            )
            result = await cursor.fetchone()
            return result if result else None

    async def update_guild_settings(
        self,
        guild_id: int,
        channel_id: Optional[int] = None,
        notification_time: Optional[str] = None,
    ) -> None:
        """Update guild notification settings."""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if settings exist
            cursor = await db.execute(
                "SELECT 1 FROM guild_settings WHERE guild_id = ?", (guild_id,)
            )
            exists = await cursor.fetchone()

            if exists:
                # Update existing settings
                updates = []
                params = []

                if channel_id is not None:
                    updates.append("notification_channel_id = ?")
                    params.append(channel_id)

                if notification_time is not None:
                    updates.append("notification_time = ?")
                    params.append(notification_time)

                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(guild_id)

                    await db.execute(
                        f"UPDATE guild_settings SET {', '.join(updates)} WHERE guild_id = ?",
                        params,
                    )
            else:
                # Insert new settings
                await db.execute(
                    """INSERT INTO guild_settings 
                       (guild_id, notification_channel_id, notification_time) 
                       VALUES (?, ?, ?)""",
                    (guild_id, channel_id, notification_time or "13:00"),
                )

            await db.commit()

    async def is_game_notified(self, game_id: str, guild_id: int) -> bool:
        """Check if a game has already been notified for a guild."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM notified_games WHERE game_id = ? AND guild_id = ?",
                (game_id, guild_id),
            )
            result = await cursor.fetchone()
            return result is not None

    async def mark_game_notified(self, game_id: str, guild_id: int) -> None:
        """Mark a game as notified for a guild."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO notified_games (game_id, guild_id) VALUES (?, ?)",
                (game_id, guild_id),
            )
            await db.commit()

    async def cleanup_old_notifications(self, days: int = 30) -> None:
        """Clean up old notification records."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM notified_games WHERE notified_at < datetime('now', '-{} days')".format(
                    days
                )
            )
            await db.commit()

    async def log_health_status(
        self, status: str, error_message: Optional[str] = None
    ) -> None:
        """Log bot health status."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO bot_health (status, error_message) VALUES (?, ?)",
                (status, error_message),
            )
            await db.commit()

    async def get_all_guild_settings(self) -> List[Tuple[int, int, str]]:
        """Get all guild settings for notifications."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT guild_id, notification_channel_id, notification_time FROM guild_settings WHERE notification_channel_id IS NOT NULL"
            )
            return await cursor.fetchall()

"""Configuration management for the Epic Games Discord Bot."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_GUILD_ID: Optional[int] = (
        int(os.getenv("DISCORD_GUILD_ID")) if os.getenv("DISCORD_GUILD_ID") else None
    )

    # Notification Configuration
    NOTIFICATION_CHANNEL_ID: Optional[int] = (
        int(os.getenv("NOTIFICATION_CHANNEL_ID"))
        if os.getenv("NOTIFICATION_CHANNEL_ID")
        else None
    )
    NOTIFICATION_TIME: str = os.getenv("NOTIFICATION_TIME", "13:00")

    # Epic Games Configuration
    EPIC_GAMES_REGION: str = os.getenv("EPIC_GAMES_REGION", "US")
    EPIC_GAMES_API_URL: str = (
        "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    )

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./data/bot.db")

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Cache Configuration
    CACHE_DURATION: int = 3600  # 1 hour in seconds

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required")
        return True

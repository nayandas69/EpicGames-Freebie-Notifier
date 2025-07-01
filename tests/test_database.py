"""Tests for database functionality."""

import pytest
import asyncio
import pytest_asyncio
import tempfile
import os
from pathlib import Path

from src.database.database import Database


class TestDatabase:
    """Test cases for database functionality."""

    @pytest_asyncio.fixture
    async def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
            db_path = tmp.name

        db = Database(db_path)
        await db.initialize()

        yield db

        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_db):
        """Test database initialization."""
        # Database should be initialized without errors
        assert temp_db is not None

    @pytest.mark.asyncio
    async def test_guild_settings_crud(self, temp_db):
        """Test guild settings CRUD operations."""
        guild_id = 12345
        channel_id = 67890
        notification_time = "14:30"

        # Test insert
        await temp_db.update_guild_settings(guild_id, channel_id, notification_time)

        # Test select
        settings = await temp_db.get_guild_settings(guild_id)
        assert settings is not None
        assert settings[0] == channel_id
        assert settings[1] == notification_time

        # Test update
        new_time = "15:45"
        await temp_db.update_guild_settings(guild_id, notification_time=new_time)

        settings = await temp_db.get_guild_settings(guild_id)
        assert settings[1] == new_time

    @pytest.mark.asyncio
    async def test_game_notification_tracking(self, temp_db):
        """Test game notification tracking."""
        game_id = "test-game-123"
        guild_id = 12345

        # Initially not notified
        assert not await temp_db.is_game_notified(game_id, guild_id)

        # Mark as notified
        await temp_db.mark_game_notified(game_id, guild_id)

        # Should now be marked as notified
        assert await temp_db.is_game_notified(game_id, guild_id)

        # Marking again should not cause errors (IGNORE constraint)
        await temp_db.mark_game_notified(game_id, guild_id)
        assert await temp_db.is_game_notified(game_id, guild_id)

    @pytest.mark.asyncio
    async def test_health_logging(self, temp_db):
        """Test health status logging."""
        await temp_db.log_health_status("healthy")
        await temp_db.log_health_status("error", "Test error message")

        # No exceptions should be raised
        assert True

    @pytest.mark.asyncio
    async def test_get_all_guild_settings(self, temp_db):
        """Test getting all guild settings."""
        # Add some test data
        await temp_db.update_guild_settings(111, 222, "10:00")
        await temp_db.update_guild_settings(333, 444, "15:00")
        await temp_db.update_guild_settings(555, None, "20:00")  # No channel

        settings = await temp_db.get_all_guild_settings()

        # Should only return guilds with notification channels
        assert len(settings) == 2
        assert (111, 222, "10:00") in settings
        assert (333, 444, "15:00") in settings

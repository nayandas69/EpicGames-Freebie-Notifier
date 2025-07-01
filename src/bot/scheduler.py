"""Task scheduler for automated notifications."""

import asyncio
from datetime import datetime, time
from typing import List, Tuple
import discord
from discord.ext import tasks

from src.services.epic_games import EpicGamesService
from src.database.database import Database
from src.bot.embeds import EmbedBuilder
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationScheduler:
    """Handles scheduled notifications for free games."""

    def __init__(self, bot: discord.Client, database: Database):
        self.bot = bot
        self.database = database
        self.notification_task.start()

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.notification_task.cancel()

    @tasks.loop(minutes=30)  # Check every 30 minutes
    async def notification_task(self):
        """Main notification task that runs periodically."""
        try:
            current_time = datetime.utcnow().time()
            guild_settings = await self.database.get_all_guild_settings()

            for guild_id, channel_id, notification_time_str in guild_settings:
                try:
                    # Parse notification time
                    hour, minute = map(int, notification_time_str.split(":"))
                    notification_time = time(hour, minute)

                    # Check if it's time to send notifications (within 30-minute window)
                    if self._is_notification_time(current_time, notification_time):
                        await self._send_guild_notifications(guild_id, channel_id)

                except Exception as e:
                    logger.error(
                        f"Error processing notifications for guild {guild_id}: {e}"
                    )
                    await self.database.log_health_status("error", str(e))

            # Cleanup old notifications
            await self.database.cleanup_old_notifications()
            await self.database.log_health_status("healthy")

        except Exception as e:
            logger.error(f"Error in notification task: {e}")
            await self.database.log_health_status("error", str(e))

    @notification_task.before_loop
    async def before_notification_task(self):
        """Wait until bot is ready before starting notifications."""
        await self.bot.wait_until_ready()
        logger.info("Notification scheduler started")

    def _is_notification_time(self, current_time: time, target_time: time) -> bool:
        """Check if current time is within notification window."""
        current_minutes = current_time.hour * 60 + current_time.minute
        target_minutes = target_time.hour * 60 + target_time.minute

        # Allow 30-minute window
        return abs(current_minutes - target_minutes) <= 15

    async def _send_guild_notifications(self, guild_id: int, channel_id: int) -> None:
        """Send notifications for a specific guild."""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                logger.warning(f"Guild {guild_id} not found")
                return

            channel = guild.get_channel(channel_id)
            if not channel:
                logger.warning(f"Channel {channel_id} not found in guild {guild_id}")
                return

            # Check channel permissions
            if not channel.permissions_for(guild.me).send_messages:
                logger.warning(
                    f"No permission to send messages in channel {channel_id}"
                )
                return

            # Fetch free games
            async with EpicGamesService() as epic_service:
                games = await epic_service.get_free_games()

            if not games:
                logger.info(f"No free games to notify for guild {guild_id}")
                return

            # Filter out already notified games
            new_games = []
            for game in games:
                if not await self.database.is_game_notified(game.id, guild_id):
                    new_games.append(game)

            if not new_games:
                logger.info(f"No new games to notify for guild {guild_id}")
                return

            # Send notifications
            embed = EmbedBuilder.create_games_list_embed(new_games)
            embed.title = "🚨 New Free Games Alert!"
            embed.description = f"**{len(new_games)} new free game{'s' if len(new_games) != 1 else ''} available on Epic Games Store!**"

            await channel.send(embed=embed)

            # Send detailed embeds for each new game
            for game in new_games[:2]:  # Limit to 2 detailed embeds
                game_embed = EmbedBuilder.create_game_embed(game)
                await channel.send(embed=game_embed)

                # Mark as notified
                await self.database.mark_game_notified(game.id, guild_id)

            logger.info(
                f"Sent notifications for {len(new_games)} games to guild {guild_id}"
            )

        except Exception as e:
            logger.error(f"Error sending notifications to guild {guild_id}: {e}")
            raise

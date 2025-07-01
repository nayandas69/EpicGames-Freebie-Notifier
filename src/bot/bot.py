"""Main Discord bot implementation."""

import discord
from discord.ext import commands
import asyncio
from typing import Optional

from src.config import Config
from src.database.database import Database
from src.bot.commands import setup as setup_commands
from src.bot.scheduler import NotificationScheduler
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/bot.log")


class EpicGamesBot(commands.Bot):
    """Epic Games Discord Bot."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )

        self.database: Optional[Database] = None
        self.scheduler: Optional[NotificationScheduler] = None

    async def setup_hook(self) -> None:
        """Set up the bot after login."""
        logger.info("Setting up bot...")

        # Initialize database
        self.database = Database()
        await self.database.initialize()

        # Set up commands
        await setup_commands(self, self.database)

        # Set up scheduler
        self.scheduler = NotificationScheduler(self, self.database)

        # Sync commands
        if Config.DISCORD_GUILD_ID:
            guild = discord.Object(id=Config.DISCORD_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(f"Synced commands to guild {Config.DISCORD_GUILD_ID}")
        else:
            await self.tree.sync()
            logger.info("Synced commands globally")

        logger.info("Bot setup complete")

    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching, name="for free Epic Games"
        )
        await self.change_presence(activity=activity)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Called when the bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")

        # Send welcome message to system channel if available
        if (
            guild.system_channel
            and guild.system_channel.permissions_for(guild.me).send_messages
        ):
            embed = discord.Embed(
                title="🎮 Epic Games Bot",
                description=(
                    "Thanks for adding me to your server!\n\n"
                    "**Commands:**\n"
                    "• `/freegames` - View current free games\n"
                    "• `/configure notification_time HH:MM` - Set notification time\n"
                    "• `/configure channel #channel` - Set notification channel\n\n"
                    "**Getting Started:**\n"
                    "1. Use `/configure channel #your-channel` to set where notifications are sent\n"
                    "2. Use `/configure notification_time 13:00` to set when to check for new games\n"
                    "3. Use `/freegames` to see current free games anytime!"
                ),
                color=0x00FF00,
            )
            embed.set_footer(text="Epic Games Store • Free Game Notifications")

            try:
                await guild.system_channel.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not send welcome message to {guild.name}")

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Called when the bot leaves a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        """Handle command errors."""
        logger.error(f"Command error in {ctx.command}: {error}")

    async def on_error(self, event: str, *args, **kwargs) -> None:
        """Handle general errors."""
        logger.error(f"Error in event {event}", exc_info=True)

    async def close(self) -> None:
        """Clean up when bot is shutting down."""
        logger.info("Bot shutting down...")

        if self.scheduler:
            self.scheduler.cog_unload()

        await super().close()


async def run_bot() -> None:
    """Run the Discord bot."""
    Config.validate()

    bot = EpicGamesBot()

    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(run_bot())

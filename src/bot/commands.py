"""Discord bot commands for the Epic Games bot."""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import re

from src.services.epic_games import EpicGamesService
from src.database.database import Database
from src.bot.embeds import EmbedBuilder
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GameCommands(commands.Cog):
    """Commands related to Epic Games functionality."""

    def __init__(self, bot: commands.Bot, database: Database):
        self.bot = bot
        self.database = database

    @app_commands.command(
        name="freegames", description="Display current free games on Epic Games Store"
    )
    async def free_games(self, interaction: discord.Interaction) -> None:
        """Display current free games."""
        await interaction.response.defer()

        try:
            async with EpicGamesService() as epic_service:
                games = await epic_service.get_free_games()

            if not games:
                embed = EmbedBuilder.create_info_embed(
                    "No Free Games",
                    "There are currently no free games available on the Epic Games Store. Check back later!",
                )
                await interaction.followup.send(embed=embed)
                return

            # Send overview embed first
            overview_embed = EmbedBuilder.create_games_list_embed(games)
            await interaction.followup.send(embed=overview_embed)

            # Send detailed embeds for each game
            for game in games[:3]:  # Limit to 3 detailed embeds to avoid spam
                game_embed = EmbedBuilder.create_game_embed(game)
                await interaction.followup.send(embed=game_embed)

            logger.info(
                f"Free games command executed by {interaction.user} in {interaction.guild}"
            )

        except Exception as e:
            logger.error(f"Error in free_games command: {e}")
            embed = EmbedBuilder.create_error_embed(
                "Error Fetching Games",
                "Sorry, I couldn't fetch the free games right now. Please try again later.",
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="configure", description="Configure bot settings")
    @app_commands.describe(setting="The setting to configure", value="The value to set")
    @app_commands.choices(
        setting=[
            app_commands.Choice(name="notification_time", value="notification_time"),
            app_commands.Choice(name="channel", value="channel"),
        ]
    )
    async def configure(
        self, interaction: discord.Interaction, setting: str, value: str
    ) -> None:
        """Configure bot settings."""
        if not interaction.user.guild_permissions.manage_guild:
            embed = EmbedBuilder.create_error_embed(
                "Permission Denied",
                "You need the 'Manage Server' permission to configure bot settings.",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            if setting == "notification_time":
                await self._configure_notification_time(interaction, value)
            elif setting == "channel":
                await self._configure_channel(interaction, value)

        except Exception as e:
            logger.error(f"Error in configure command: {e}")
            embed = EmbedBuilder.create_error_embed(
                "Configuration Error",
                "An error occurred while updating the configuration. Please try again.",
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def _configure_notification_time(
        self, interaction: discord.Interaction, time_str: str
    ) -> None:
        """Configure notification time."""
        # Validate time format (HH:MM)
        time_pattern = re.compile(r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
        if not time_pattern.match(time_str):
            embed = EmbedBuilder.create_error_embed(
                "Invalid Time Format",
                "Please use HH:MM format (24-hour). Example: 13:00 for 1:00 PM",
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        await self.database.update_guild_settings(
            interaction.guild.id, notification_time=time_str
        )

        embed = EmbedBuilder.create_success_embed(
            "Notification Time Updated",
            f"Daily notifications will now be sent at {time_str} UTC.",
        )
        await interaction.followup.send(embed=embed)

        logger.info(
            f"Notification time set to {time_str} for guild {interaction.guild.id}"
        )

    async def _configure_channel(
        self, interaction: discord.Interaction, channel_mention: str
    ) -> None:
        """Configure notification channel."""
        # Extract channel ID from mention
        channel_id_match = re.search(r"<#(\d+)>", channel_mention)
        if not channel_id_match:
            embed = EmbedBuilder.create_error_embed(
                "Invalid Channel", "Please mention a valid channel using #channel-name"
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        channel_id = int(channel_id_match.group(1))
        channel = interaction.guild.get_channel(channel_id)

        if not channel:
            embed = EmbedBuilder.create_error_embed(
                "Channel Not Found",
                "The specified channel could not be found in this server.",
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Check if bot has permission to send messages in the channel
        if not channel.permissions_for(interaction.guild.me).send_messages:
            embed = EmbedBuilder.create_error_embed(
                "Permission Error",
                f"I don't have permission to send messages in {channel.mention}. Please check my permissions.",
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        await self.database.update_guild_settings(
            interaction.guild.id, channel_id=channel_id
        )

        embed = EmbedBuilder.create_success_embed(
            "Notification Channel Updated",
            f"Free game notifications will now be sent to {channel.mention}.",
        )
        await interaction.followup.send(embed=embed)

        logger.info(
            f"Notification channel set to {channel_id} for guild {interaction.guild.id}"
        )


async def setup(bot: commands.Bot, database: Database) -> None:
    """Set up the commands cog."""
    await bot.add_cog(GameCommands(bot, database))

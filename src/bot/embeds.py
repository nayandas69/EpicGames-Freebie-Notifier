"""Discord embed utilities for the Epic Games bot."""

import discord
from typing import List
from datetime import datetime

from src.models.game import Game


class EmbedBuilder:
    """Builder for Discord embeds."""

    @staticmethod
    def create_game_embed(game: Game) -> discord.Embed:
        """Create a rich embed for a single game."""
        # Determine embed color based on game status
        color = 0x00FF00 if game.is_free_now else 0xFF0000

        embed = discord.Embed(
            title=game.title,
            description=(
                game.description[:500] + "..."
                if len(game.description) > 500
                else game.description
            ),
            color=color,
            url=game.store_url,
            timestamp=datetime.utcnow(),
        )

        # Add cover image
        if game.cover_image:
            embed.set_image(url=game.cover_image)

        # Add game info fields
        embed.add_field(name="🏢 Publisher", value=game.publisher, inline=True)

        embed.add_field(name="👨‍💻 Developer", value=game.developer, inline=True)

        # Add pricing info
        if game.price.original_price > 0:
            original_price = f"${game.price.original_price / 100:.2f}"
            embed.add_field(name="💰 Original Price", value=original_price, inline=True)

        # Add promotion info
        if game.promotion and game.promotion.is_active:
            embed.add_field(
                name="⏰ Time Remaining",
                value=game.promotion.time_remaining,
                inline=True,
            )

            embed.add_field(
                name="📅 Promotion Ends",
                value=f"<t:{int(game.promotion.end_date.timestamp())}:R>",
                inline=True,
            )

        # Add categories
        if game.categories:
            categories_str = ", ".join(game.categories[:5])  # Limit to 5 categories
            embed.add_field(name="🏷️ Categories", value=categories_str, inline=False)

        # Add store link as button-like text
        embed.add_field(
            name="🔗 Epic Games Store",
            value=f"[Click here to view in store]({game.store_url})",
            inline=False,
        )

        embed.set_footer(
            text="Epic Games Store • Free Game Alert",
            icon_url="https://avatars.githubusercontent.com/u/174907517?v=4",
        )

        return embed

    @staticmethod
    def create_games_list_embed(games: List[Game]) -> discord.Embed:
        """Create an embed showing multiple games."""
        if not games:
            embed = discord.Embed(
                title="🎮 Free Games on Epic Games Store",
                description="No free games available right now. Check back later!",
                color=0xFF9900,
                timestamp=datetime.utcnow(),
            )
        else:
            embed = discord.Embed(
                title="🎮 Free Games on Epic Games Store",
                description=f"Found {len(games)} free game{'s' if len(games) != 1 else ''} available now!",
                color=0x00FF00,
                timestamp=datetime.utcnow(),
            )

            for i, game in enumerate(games[:5], 1):  # Limit to 5 games
                time_remaining = ""
                if game.promotion and game.promotion.is_active:
                    time_remaining = f"\n⏰ {game.promotion.time_remaining} remaining"

                embed.add_field(
                    name=f"{i}. {game.title}",
                    value=f"🏢 {game.publisher}{time_remaining}\n[View in Store]({game.store_url})",
                    inline=False,
                )

        embed.set_footer(
            text="Epic Games Store • Use /freegames for detailed view",
            icon_url="https://avatars.githubusercontent.com/u/174907517?v=4",
        )

        return embed

    @staticmethod
    def create_error_embed(title: str, description: str) -> discord.Embed:
        """Create an error embed."""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=0xFF0000,
            timestamp=datetime.utcnow(),
        )
        return embed

    @staticmethod
    def create_success_embed(title: str, description: str) -> discord.Embed:
        """Create a success embed."""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=0x00FF00,
            timestamp=datetime.utcnow(),
        )
        return embed

    @staticmethod
    def create_info_embed(title: str, description: str) -> discord.Embed:
        """Create an info embed."""
        embed = discord.Embed(
            title=f"ℹ️ {title}",
            description=description,
            color=0x0099FF,
            timestamp=datetime.utcnow(),
        )
        return embed

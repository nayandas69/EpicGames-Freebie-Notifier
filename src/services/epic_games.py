"""Epic Games Store API service."""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Optional
from urllib.parse import quote

from src.config import Config
from src.models.game import Game, GameImage, GamePrice, GamePromotion
from src.utils.logger import setup_logger
from src.utils.cache import Cache

logger = setup_logger(__name__)


class EpicGamesService:
    """Service for interacting with Epic Games Store API."""

    def __init__(self):
        self.cache = Cache()
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "Epic Games Discord Bot/1.0.0"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_free_games(self, use_cache: bool = True) -> List[Game]:
        """Fetch current free games from Epic Games Store."""
        cache_key = f"free_games_{Config.EPIC_GAMES_REGION}"

        if use_cache:
            cached_games = await self.cache.get(cache_key)
            if cached_games:
                logger.info("Returning cached free games")
                return cached_games

        try:
            if not self.session:
                raise RuntimeError(
                    "Service not initialized. Use async context manager."
                )

            params = {
                "locale": "en-US",
                "country": Config.EPIC_GAMES_REGION,
                "allowCountries": Config.EPIC_GAMES_REGION,
            }

            logger.info(f"Fetching free games from Epic Games API")
            async with self.session.get(
                Config.EPIC_GAMES_API_URL, params=params
            ) as response:
                response.raise_for_status()
                data = await response.json()

            games = self._parse_games_data(data)
            free_games = [game for game in games if game.is_free_now]

            # Cache the results
            await self.cache.set(cache_key, free_games, Config.CACHE_DURATION)

            logger.info(f"Found {len(free_games)} free games")
            return free_games

        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching free games: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching free games: {e}")
            raise

    def _parse_games_data(self, data: dict) -> List[Game]:
        """Parse Epic Games API response into Game objects."""
        games = []

        try:
            elements = (
                data.get("data", {})
                .get("Catalog", {})
                .get("searchStore", {})
                .get("elements", [])
            )

            for element in elements:
                try:
                    game = self._parse_game_element(element)
                    if game:
                        games.append(game)
                except Exception as e:
                    logger.warning(f"Error parsing game element: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing games data: {e}")

        return games

    def _parse_game_element(self, element: dict) -> Optional[Game]:
        """Parse a single game element from the API response."""
        try:
            # Basic game info
            game_id = element.get("id", "")
            title = element.get("title", "Unknown Title")
            description = element.get("description", "")

            # Publisher and developer info
            seller = element.get("seller", {})
            publisher = seller.get("name", "Unknown Publisher")
            developer = publisher  # Epic API doesn't always separate these

            # Categories
            categories = [cat.get("path", "") for cat in element.get("categories", [])]

            # Images
            images = []
            for img in element.get("keyImages", []):
                images.append(
                    GameImage(type=img.get("type", ""), url=img.get("url", ""))
                )

            # Pricing
            price_info = element.get("price", {})
            total_price = price_info.get("totalPrice", {})

            price = GamePrice(
                original_price=total_price.get("originalPrice", 0),
                discount_price=total_price.get("discountPrice", 0),
                currency_code=total_price.get("currencyCode", "USD"),
            )

            # Promotions
            promotion = None
            promotions = element.get("promotions", {}).get("promotionalOffers", [])
            if promotions and promotions[0].get("promotionalOffers"):
                promo_data = promotions[0]["promotionalOffers"][0]

                start_date = datetime.fromisoformat(
                    promo_data.get("startDate", "").replace("Z", "+00:00")
                )
                end_date = datetime.fromisoformat(
                    promo_data.get("endDate", "").replace("Z", "+00:00")
                )

                promotion = GamePromotion(start_date=start_date, end_date=end_date)

            # Store URL
            url_slug = element.get("urlSlug", "") or element.get("productSlug", "")
            store_url = (
                f"https://store.epicgames.com/en-US/p/{quote(url_slug)}"
                if url_slug
                else ""
            )

            return Game(
                id=game_id,
                title=title,
                description=description,
                publisher=publisher,
                developer=developer,
                categories=categories,
                images=images,
                price=price,
                promotion=promotion,
                store_url=store_url,
            )

        except Exception as e:
            logger.error(f"Error parsing game element: {e}")
            return None

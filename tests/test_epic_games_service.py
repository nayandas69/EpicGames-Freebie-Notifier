"""Tests for Epic Games service."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.services.epic_games import EpicGamesService
from src.models.game import Game, GamePrice, GamePromotion


class TestEpicGamesService:
    """Test cases for Epic Games service."""

    @pytest.fixture
    def mock_api_response(self):
        """Mock API response data."""
        return {
            "data": {
                "Catalog": {
                    "searchStore": {
                        "elements": [
                            {
                                "id": "test-game-1",
                                "title": "Test Game 1",
                                "description": "A test game",
                                "seller": {"name": "Test Publisher"},
                                "categories": [{"path": "games/action"}],
                                "keyImages": [
                                    {
                                        "type": "DieselStoreFrontWide",
                                        "url": "https://example.com/image.jpg",
                                    }
                                ],
                                "price": {
                                    "totalPrice": {
                                        "originalPrice": 2999,
                                        "discountPrice": 0,
                                        "currencyCode": "USD",
                                    }
                                },
                                "promotions": {
                                    "promotionalOffers": [
                                        {
                                            "promotionalOffers": [
                                                {
                                                    "startDate": "2024-01-01T00:00:00.000Z",
                                                    "endDate": "2024-12-31T23:59:59.000Z",
                                                }
                                            ]
                                        }
                                    ]
                                },
                                "urlSlug": "test-game-1",
                            }
                        ]
                    }
                }
            }
        }

    @pytest.mark.asyncio
    async def test_get_free_games_success(self, mock_api_response):
        """Test successful free games retrieval."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_api_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value.__aenter__.return_value = mock_response

            async with EpicGamesService() as service:
                games = await service.get_free_games(use_cache=False)

            assert len(games) == 1
            assert games[0].title == "Test Game 1"
            assert games[0].is_free_now

    @pytest.mark.asyncio
    async def test_get_free_games_cache(self, mock_api_response):
        """Test cache functionality."""
        cached_games = [
            Game(
                id="cached-game",
                title="Cached Game",
                description="From cache",
                publisher="Cache Publisher",
                developer="Cache Developer",
                categories=[],
                images=[],
                price=GamePrice(0, 0, "USD"),
                promotion=GamePromotion(datetime(2024, 1, 1), datetime(2024, 12, 31)),
                store_url="https://example.com",
            )
        ]

        async with EpicGamesService() as service:
            await service.cache.set("free_games_US", cached_games, 3600)
            games = await service.get_free_games(use_cache=True)

        assert len(games) == 1
        assert games[0].title == "Cached Game"

    @pytest.mark.asyncio
    async def test_parse_games_data_empty(self):
        """Test parsing empty API response."""
        async with EpicGamesService() as service:
            games = service._parse_games_data({"data": {}})

        assert games == []

    def test_parse_game_element_invalid(self):
        """Test parsing invalid game element."""
        service = EpicGamesService()
        game = service._parse_game_element({})

        assert game is not None
        assert game.title == "Unknown Title"
        assert game.publisher == "Unknown Publisher"

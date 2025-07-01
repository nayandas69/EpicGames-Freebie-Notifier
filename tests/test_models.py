"""Tests for game models."""

import pytest
from datetime import datetime, timedelta

from src.models.game import Game, GamePrice, GamePromotion, GameImage


class TestGameModels:
    """Test cases for game models."""

    def test_game_price_is_free(self):
        """Test GamePrice.is_free property."""
        free_price = GamePrice(2999, 0, "USD")
        paid_price = GamePrice(2999, 1999, "USD")

        assert free_price.is_free
        assert not paid_price.is_free

    def test_game_promotion_is_active(self):
        """Test GamePromotion.is_active property."""
        now = datetime.utcnow()

        # Active promotion
        active_promo = GamePromotion(
            start_date=now - timedelta(hours=1), end_date=now + timedelta(hours=1)
        )

        # Expired promotion
        expired_promo = GamePromotion(
            start_date=now - timedelta(hours=2), end_date=now - timedelta(hours=1)
        )

        # Future promotion
        future_promo = GamePromotion(
            start_date=now + timedelta(hours=1), end_date=now + timedelta(hours=2)
        )

        assert active_promo.is_active
        assert not expired_promo.is_active
        assert not future_promo.is_active

    def test_game_promotion_time_remaining(self):
        """Test GamePromotion.time_remaining property."""
        now = datetime.utcnow()

        # Active promotion with 2 hours remaining
        active_promo = GamePromotion(
            start_date=now - timedelta(hours=1), end_date=now + timedelta(hours=2)
        )

        # Expired promotion
        expired_promo = GamePromotion(
            start_date=now - timedelta(hours=2), end_date=now - timedelta(hours=1)
        )

        time_remaining = active_promo.time_remaining
        assert (
            "2h" in time_remaining or "1h" in time_remaining
        )  # Allow for timing variations

        assert expired_promo.time_remaining == "Promotion ended"

    def test_game_cover_image(self):
        """Test Game.cover_image property."""
        images = [
            GameImage("Screenshot", "https://example.com/screenshot.jpg"),
            GameImage("DieselStoreFrontWide", "https://example.com/cover.jpg"),
            GameImage("Logo", "https://example.com/logo.jpg"),
        ]

        game = Game(
            id="test",
            title="Test Game",
            description="Test",
            publisher="Test Publisher",
            developer="Test Developer",
            categories=[],
            images=images,
            price=GamePrice(0, 0, "USD"),
            promotion=None,
            store_url="https://example.com",
        )

        assert game.cover_image == "https://example.com/cover.jpg"

    def test_game_is_free_now(self):
        """Test Game.is_free_now property."""
        now = datetime.utcnow()

        free_game = Game(
            id="test",
            title="Test Game",
            description="Test",
            publisher="Test Publisher",
            developer="Test Developer",
            categories=[],
            images=[],
            price=GamePrice(2999, 0, "USD"),
            promotion=GamePromotion(
                start_date=now - timedelta(hours=1), end_date=now + timedelta(hours=1)
            ),
            store_url="https://example.com",
        )

        paid_game = Game(
            id="test2",
            title="Test Game 2",
            description="Test",
            publisher="Test Publisher",
            developer="Test Developer",
            categories=[],
            images=[],
            price=GamePrice(2999, 1999, "USD"),
            promotion=None,
            store_url="https://example.com",
        )

        assert free_game.is_free_now
        assert not paid_game.is_free_now

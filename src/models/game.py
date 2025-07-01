"""Game model for Epic Games Store data."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timezone

@dataclass
class GameImage:
    """Represents a game image."""

    type: str
    url: str


@dataclass
class GamePrice:
    """Represents game pricing information."""

    original_price: int
    discount_price: int
    currency_code: str

    @property
    def is_free(self) -> bool:
        """Check if the game is currently free."""
        return self.discount_price == 0


@dataclass
class GamePromotion:
    """Represents a game promotion period."""

    start_date: datetime
    end_date: datetime

    @property
    def is_active(self) -> bool:
        """Check if the promotion is currently active."""
        now = datetime.now(timezone.utc)
        return self.start_date <= now <= self.end_date

    @property
    def time_remaining(self) -> str:
        """Get human-readable time remaining."""
        if not self.is_active:
            return "Promotion ended"

        remaining = self.end_date - datetime.utcnow()
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


@dataclass
class Game:
    """Represents an Epic Games Store game."""

    id: str
    title: str
    description: str
    publisher: str
    developer: str
    categories: List[str]
    images: List[GameImage]
    price: GamePrice
    promotion: Optional[GamePromotion]
    store_url: str

    @property
    def cover_image(self) -> Optional[str]:
        """Get the cover image URL."""
        for image in self.images:
            if image.type in ["DieselStoreFrontWide", "OfferImageWide"]:
                return image.url
        return self.images[0].url if self.images else None

    @property
    def is_free_now(self) -> bool:
        """Check if the game is currently free."""
        return self.price.is_free and self.promotion and self.promotion.is_active

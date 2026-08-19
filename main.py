"""
Epic Games Freebie Notifier

Author: nayandas69
GitHub: https://github.com/nayandas69/EpicGames-Freebie-Notifier
Description: Python script that monitors the Epic Games Store for free games
             and sends Discord notifications via webhook.

Features:
    - Fetches free games from the Epic Games Store API
    - Prevents duplicate notifications with persistent storage
    - Rich Discord embeds with game details and countdown
    - Resilient HTTP requests with automatic retries
    - Environment variable configuration
    - Comprehensive error handling and logging
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

load_dotenv(override=True, dotenv_path=Path(".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("epic_notifier.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()
POSTED_FILE = Path("epics.json")
EPIC_GAMES_API = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
)
EPIC_STORE_BASE = "https://store.epicgames.com/en-US/p/"
REQUEST_TIMEOUT = 30  # seconds
EPIC_BLUE = 0x0078F2

PREFERRED_IMAGE_TYPES = (
    "DieselStoreFrontWide",
    "OfferImageWide",
    "featuredMedia",
    "Thumbnail",
)


# ---------------------------------------------------------------------------
# HTTP session with retries
# ---------------------------------------------------------------------------
def build_session() -> requests.Session:
    """Creates a requests session with sensible retry/backoff behavior."""
    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "EpicGames-Freebie-Notifier/2.0"})
    return session


SESSION = build_session()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate_environment() -> bool:
    """Validates that a usable Discord webhook is configured."""
    if not DISCORD_WEBHOOK:
        logger.error(
            "DISCORD_WEBHOOK is not configured. Set it in a .env file or as an "
            "environment variable. Get the URL from Discord: Server Settings > "
            "Integrations > Webhooks > New Webhook > Copy Webhook URL."
        )
        return False

    if not DISCORD_WEBHOOK.startswith("https://discord.com/api/webhooks/"):
        logger.error(
            "DISCORD_WEBHOOK looks invalid. It should start with "
            "'https://discord.com/api/webhooks/'."
        )
        return False

    logger.info("Configuration validated successfully.")
    return True


# ---------------------------------------------------------------------------
# Fetching & parsing
# ---------------------------------------------------------------------------
def get_free_games() -> list[dict[str, Any]]:
    """Fetches currently-free games from the Epic Games Store API."""
    try:
        response = SESSION.get(EPIC_GAMES_API, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        elements = (
            response.json()["data"]["Catalog"]["searchStore"]["elements"]
        )
    except requests.RequestException as exc:
        logger.error("Failed to fetch games from Epic Games API: %s", exc)
        raise
    except (KeyError, ValueError) as exc:
        logger.error("Failed to parse API response: %s", exc)
        raise

    free_games: list[dict[str, Any]] = []
    for element in elements:
        if not _is_currently_free(element):
            continue
        game = _extract_game_data(element)
        if game:
            free_games.append(game)

    logger.info("Found %d free game(s).", len(free_games))
    return free_games


def _is_currently_free(game: dict[str, Any]) -> bool:
    """Returns True if the game's discounted price is 0 with an active promo."""
    try:
        if game["price"]["totalPrice"]["discountPrice"] != 0:
            return False
    except (KeyError, TypeError):
        return False

    promotions = game.get("promotions") or {}
    active = promotions.get("promotionalOffers") or []
    return bool(active)


def _resolve_slug(game: dict[str, Any]) -> Optional[str]:
    """Determines the best product slug for building a store URL."""
    if game.get("productSlug"):
        return game["productSlug"]

    for key in ("catalogNs", "offerMappings"):
        source = game.get(key) or {}
        mappings = (
            source.get("mappings") if key == "catalogNs" else game.get(key)
        )
        if mappings:
            slug = mappings[0].get("pageSlug")
            if slug:
                return slug

    if game.get("urlSlug"):
        return game["urlSlug"]

    return game.get("id") or None


def _resolve_image(game: dict[str, Any]) -> str:
    """Picks the most presentable key image for the game."""
    key_images = game.get("keyImages") or []
    for wanted in PREFERRED_IMAGE_TYPES:
        for img in key_images:
            if img.get("type") == wanted and img.get("url"):
                return img["url"]
    return key_images[0].get("url", "") if key_images else ""


def _resolve_original_price(game: dict[str, Any]) -> str:
    """Extracts a human-readable original price, defaulting to 'Free'."""
    try:
        price_info = game.get("price", {}).get("totalPrice", {})
        original = price_info.get("originalPrice", 0)
        discount = price_info.get("discountPrice", 0)

        if original and original > discount:
            return f"${original / 100:.2f}"

        fmt = price_info.get("fmtPrice", {}).get("originalPrice")
        if fmt and fmt != "0":
            return fmt
    except (KeyError, AttributeError, TypeError):
        pass
    return "Free"


def _extract_game_data(game: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Extracts the fields we care about from a raw API game element."""
    try:
        title = game["title"]
        if "mystery" in title.lower():
            logger.debug("Skipping mystery game: %s", title)
            return None

        slug = _resolve_slug(game)
        if not slug:
            logger.warning("Could not determine product slug for '%s'.", title)
            return None

        return {
            "title": title,
            "url": f"{EPIC_STORE_BASE}{slug}",
            "image": _resolve_image(game),
            "original_price": _resolve_original_price(game),
            "end_timestamp": _calculate_expiration_timestamp(game),
        }
    except (KeyError, IndexError, AttributeError) as exc:
        logger.warning(
            "Failed to extract data for '%s': %s",
            game.get("title", "Unknown"),
            exc,
        )
        return None


def _calculate_expiration_timestamp(game: dict[str, Any]) -> Optional[int]:
    """Returns the Unix timestamp for when the free promotion ends."""
    promotions = game.get("promotions") or {}
    for key in ("promotionalOffers", "upcomingPromotionalOffers"):
        groups = promotions.get(key) or []
        if not groups:
            continue
        offers = groups[0].get("promotionalOffers") or []
        if not offers:
            continue
        end_date = offers[0].get("endDate")
        if not end_date:
            continue
        try:
            end = dt.datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            return int(end.timestamp())
        except (ValueError, AttributeError):
            continue
    return None


def _format_expiration_date(timestamp: Optional[int]) -> str:
    """Formats an expiration timestamp into a human-readable date."""
    if not timestamp:
        return "Unknown"
    date = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
    return date.strftime("%d %B %Y")


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
def load_posted_games() -> dict[str, Any]:
    """Loads previously-notified games from persistent storage."""
    if not POSTED_FILE.exists():
        return {}
    try:
        with POSTED_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, IOError) as exc:
        logger.error("Failed to load posted games file: %s", exc)
        return {}


def save_posted_games(posted: dict[str, Any]) -> None:
    """Persists posted games to prevent duplicate notifications."""
    try:
        with POSTED_FILE.open("w", encoding="utf-8") as fh:
            json.dump(posted, fh, indent=4, ensure_ascii=False)
        logger.debug("Saved %d game(s) to tracking file.", len(posted))
    except IOError as exc:
        logger.error("Failed to save posted games file: %s", exc)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
def send_discord_notification(game: dict[str, Any]) -> bool:
    """Sends a rich embed notification to the Discord webhook."""
    embed: dict[str, Any] = {
        "title": f"{game['title']} (Epic Games) Giveaway",
        "description": f"**[Claim Now]({game['url']})**",
        "url": game["url"],
        "color": EPIC_BLUE,
        "fields": [
            {"name": "Price", "value": game["original_price"], "inline": True},
            {
                "name": "Free until",
                "value": _format_expiration_date(game["end_timestamp"]),
                "inline": True,
            },
        ],
    }
    if game.get("image"):
        embed["image"] = {"url": game["image"]}

    try:
        response = SESSION.post(
            DISCORD_WEBHOOK, json={"embeds": [embed]}, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        logger.info("Successfully notified: %s", game["title"])
        return True
    except requests.RequestException as exc:
        logger.error(
            "Failed to send Discord notification for '%s': %s",
            game["title"],
            exc,
        )
        return False


# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------
def _is_game_expired(end_timestamp: Optional[int]) -> bool:
    """Returns True if the promotion end time is in the past."""
    if not end_timestamp:
        return False
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    return now >= end_timestamp


def cleanup_expired_games(
    posted_games: dict[str, Any], current_games: list[dict[str, Any]]
) -> dict[str, Any]:
    """Removes expired / no-longer-free games from tracking storage."""
    current_titles = {game["title"] for game in current_games}
    stale = [
        title
        for title, data in posted_games.items()
        if _is_game_expired(data.get("end_timestamp"))
        or title not in current_titles
    ]
    for title in stale:
        logger.info("Removing expired game from tracking: %s", title)
        del posted_games[title]
    return posted_games


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Orchestrates the notification workflow."""
    logger.info("Starting Epic Games Freebie Notifier.")

    if not validate_environment():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)

    try:
        free_games = get_free_games()
        if not free_games:
            logger.info("No free games found at this time.")
            return

        posted_games = load_posted_games()
        now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

        for game in free_games:
            title = game["title"]
            if title in posted_games:
                continue
            logger.info("New free game detected: %s", title)
            if send_discord_notification(game):
                posted_games[title] = {
                    "end_timestamp": game["end_timestamp"],
                    "notified_at": now_iso,
                }

        posted_games = cleanup_expired_games(posted_games, free_games)
        save_posted_games(posted_games)
        logger.info("Completed notification check.")
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.exception("Unexpected error occurred: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Epic Games Freebie Notifier

Author: nayandas69
GitHub: https://github.com/nayandas69/EpicGames-Freebie-Notifier
Description: Python script that monitors Epic Games Store for free games
             and sends Discord notifications via webhook.

Features:
    - Fetches free games from Epic Games Store API
    - Prevents duplicate notifications with persistent storage
    - Rich Discord embeds with game details and countdown
    - Environment variable configuration
    - Comprehensive error handling and logging
"""

import datetime
import json
import logging
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(override=True, dotenv_path=Path('.env'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('epic_notifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
POSTED_FILE = Path("epics.json")
EPIC_GAMES_API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
REQUEST_TIMEOUT = 30  # seconds


def validate_environment() -> bool:
    """
    Validates required environment variables are configured.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    env_file = Path(".env")
    logger.info(f"Current working directory: {Path.cwd()}")
    logger.info(f"Looking for .env file at: {env_file.absolute()}")
    logger.info(f".env file exists: {env_file.exists()}")
    
    if env_file.exists():
        logger.info(f".env file size: {env_file.stat().st_size} bytes")
        # Read and log the content (masking sensitive data)
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'DISCORD_WEBHOOK' in content:
                    logger.info(".env file contains DISCORD_WEBHOOK variable")
                else:
                    logger.warning(".env file does NOT contain DISCORD_WEBHOOK variable")
        except Exception as e:
            logger.error(f"Could not read .env file: {e}")
    
    if not DISCORD_WEBHOOK:
        logger.error("=" * 80)
        logger.error("ERROR: DISCORD_WEBHOOK is not configured!")
        logger.error("=" * 80)
        logger.error("")
        logger.error("Please follow these steps:")
        logger.error("1. Create a file named '.env' in this folder:")
        logger.error(f"   {Path.cwd()}")
        logger.error("")
        logger.error("2. Add this line to the .env file:")
        logger.error("   DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL")
        logger.error("")
        logger.error("3. Get your webhook URL from Discord:")
        logger.error("   - Open Discord Server Settings")
        logger.error("   - Go to Integrations > Webhooks")
        logger.error("   - Create New Webhook")
        logger.error("   - Copy Webhook URL")
        logger.error("")
        
        if not env_file.exists():
            logger.error(f"NOTE: .env file does NOT exist at: {env_file.absolute()}")
        else:
            logger.error(f"NOTE: .env file exists but DISCORD_WEBHOOK is not set inside it")
        
        logger.error("=" * 80)
        return False
    
    if "YOUR_WEBHOOK" in DISCORD_WEBHOOK or not DISCORD_WEBHOOK.startswith("https://discord.com/api/webhooks/"):
        logger.error("=" * 80)
        logger.error("ERROR: DISCORD_WEBHOOK appears to be invalid!")
        logger.error("=" * 80)
        logger.error("")
        logger.error(f"Current value: {DISCORD_WEBHOOK}")
        logger.error("")
        logger.error("Your webhook URL should look like:")
        logger.error("https://discord.com/api/webhooks/1234567890/AbCdEfGhIjKlMnOp...")
        logger.error("")
        logger.error("Please update your .env file with a valid Discord webhook URL")
        logger.error("=" * 80)
        return False
    
    logger.info("Configuration validated successfully")
    logger.info(f"Using webhook: {DISCORD_WEBHOOK[:30]}...")  # Show first 30 chars for verification
    return True


def get_free_games() -> List[Dict]:
    """
    Fetches currently free games from Epic Games Store API.

    Returns:
        List[Dict]: List of free games with details (title, URL, image, price, expiration)
    
    Raises:
        requests.RequestException: If API request fails
    """
    try:
        response = requests.get(EPIC_GAMES_API, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        games = data["data"]["Catalog"]["searchStore"]["elements"]
        
        free_games = []
        for game in games:
            # Only process games that are currently free
            if game["price"]["totalPrice"]["discountPrice"] == 0:
                game_data = _extract_game_data(game)
                if game_data:
                    free_games.append(game_data)
        
        logger.info(f"Found {len(free_games)} free game(s)")
        return free_games
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch games from Epic Games API: {e}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Failed to parse API response: {e}")
        raise


def _extract_game_data(game: Dict) -> Optional[Dict]:
    """
    Extracts relevant game information from API response.
    
    Args:
        game: Raw game data from Epic Games API
    
    Returns:
        Optional[Dict]: Processed game data or None if extraction fails
    """
    try:
        logger.debug(f"Processing game: {game.get('title', 'Unknown')}")
        
        title = game["title"]
        
        if "mystery" in title.lower():
            logger.debug(f"Skipping mystery game: {title}")
            return None
        
        product_slug = None
        
        if game.get("productSlug"):
            product_slug = game["productSlug"]
        
        elif game.get("catalogNs", {}).get("mappings"):
            mappings = game["catalogNs"]["mappings"]
            if mappings and len(mappings) > 0:
                product_slug = mappings[0].get("pageSlug")
        
        elif game.get("offerMappings"):
            mappings = game["offerMappings"]
            if mappings and len(mappings) > 0:
                product_slug = mappings[0].get("pageSlug")
        
        elif game.get("urlSlug"):
            product_slug = game["urlSlug"]
        
        if not product_slug:
            product_slug = game.get("id", "")
            logger.warning(f"Using game ID as slug for '{title}': {product_slug}")
        
        if not product_slug:
            logger.warning(f"Could not determine product slug for '{title}'")
            return None
        
        url = f"https://store.epicgames.com/en-US/p/{product_slug}"
        
        image = ""
        if game.get("keyImages"):
            for img in game["keyImages"]:
                if img.get("type") in ["DieselStoreFrontWide", "OfferImageWide", "featuredMedia"]:
                    image = img.get("url", "")
                    break
            if not image and game["keyImages"]:
                image = game["keyImages"][0].get("url", "")
        
        original_price = "Free"
        try:
            price_info = game.get("price", {}).get("totalPrice", {})
            
            # First check originalPrice in cents
            original_amount = price_info.get("originalPrice", 0)
            discount_amount = price_info.get("discountPrice", 0)
            
            # If originalPrice exists and is greater than discountPrice (meaning there was a discount)
            if original_amount and original_amount > discount_amount:
                formatted_price = original_amount / 100
                original_price = f"${formatted_price:.2f}"
            # Otherwise check the formatted price object
            elif price_info.get("fmtPrice", {}).get("originalPrice"):
                fmt_original = price_info["fmtPrice"]["originalPrice"]
                if fmt_original and fmt_original != "0":
                    original_price = fmt_original
            # Last resort: check lineOffers for original price
            elif game.get("price", {}).get("lineOffers"):
                line_offers = game["price"]["lineOffers"]
                if line_offers and len(line_offers) > 0:
                    line_price = line_offers[0].get("appliedRules", [{}])[0].get("originalPrice", 0)
                    if line_price and line_price > 0:
                        formatted_price = line_price / 100
                        original_price = f"${formatted_price:.2f}"
                
        except (KeyError, AttributeError, TypeError, IndexError) as e:
            logger.debug(f"Could not extract price for '{title}': {e}")
            original_price = "Free"
        
        end_timestamp = _calculate_expiration_timestamp(game)
        
        return {
            "title": title,
            "url": url,
            "image": image,
            "original_price": original_price,
            "end_timestamp": end_timestamp,
        }
    except (KeyError, IndexError, AttributeError) as e:
        logger.warning(f"Failed to extract data for '{game.get('title', 'Unknown')}': {e}")
        logger.debug(f"Game data structure: {json.dumps(game, indent=2)[:500]}")
        return None


def _calculate_expiration_timestamp(game: Dict) -> Optional[int]:
    """
    Calculates Unix timestamp for when the free promotion expires.

    Args:
        game: Game data from Epic Games API

    Returns:
        Optional[int]: Unix timestamp of expiration, or None if unavailable
    """
    try:
        promotions = game.get("promotions")
        
        if not promotions:
            logger.debug(f"No promotions data for game: {game.get('title')}")
            return None
        
        promo_offers = promotions.get("promotionalOffers")
        if promo_offers and len(promo_offers) > 0:
            offers = promo_offers[0].get("promotionalOffers", [])
            if offers and len(offers) > 0:
                end_date = offers[0].get("endDate")
                if end_date:
                    end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    return int(end_datetime.timestamp())
        
        upcoming = promotions.get("upcomingPromotionalOffers")
        if upcoming and len(upcoming) > 0:
            offers = upcoming[0].get("promotionalOffers", [])
            if offers and len(offers) > 0:
                end_date = offers[0].get("endDate")
                if end_date:
                    end_datetime = datetime.datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    return int(end_datetime.timestamp())
        
        logger.debug(f"Could not determine expiration for game: {game.get('title')}")
        return None
        
    except (KeyError, IndexError, ValueError, AttributeError) as e:
        logger.debug(f"Error calculating expiration for game: {e}")
        return None


def _format_expiration_date(timestamp: Optional[int]) -> str:
    """
    Formats expiration timestamp into human-readable date.
    
    Args:
        timestamp: Unix timestamp of expiration
    
    Returns:
        str: Formatted date string like "22 December 2025"
    """
    if not timestamp:
        return "Unknown"
    
    expiration_date = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    return expiration_date.strftime("%d %B %Y")


def load_posted_games() -> Dict:
    """
    Loads previously notified games from persistent storage.

    Returns:
        Dict: Previously posted games with their expiration timestamps
    """
    if POSTED_FILE.exists():
        try:
            with open(POSTED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load posted games file: {e}")
            return {}
    return {}


def save_posted_games(posted: Dict) -> None:
    """
    Persists posted games to storage to prevent duplicate notifications.

    Args:
        posted: Dictionary of posted games with their metadata
    """
    try:
        with open(POSTED_FILE, 'w', encoding='utf-8') as f:
            json.dump(posted, f, indent=4, ensure_ascii=False)
        logger.debug(f"Saved {len(posted)} game(s) to tracking file")
    except IOError as e:
        logger.error(f"Failed to save posted games file: {e}")


def send_discord_notification(game: Dict) -> bool:
    """
    Sends rich embed notification to Discord webhook.

    Args:
        game: Game details to send

    Returns:
        bool: True if notification sent successfully, False otherwise
    """
    expiration_text = _format_expiration_date(game['end_timestamp'])
    
    # Build the Discord embed payload
    embed_data = {
        "title": f"{game['title']} (Epic Games) Giveaway",
        "description": f"**[🎮 Claim Now]({game['url']})**",
        "color": 0x0078F2,  # Epic Games blue color
        "fields": [
            {
                "name": "Price",
                "value": game['original_price'],
                "inline": True
            },
            {
                "name": "Free until",
                "value": expiration_text,
                "inline": True
            }
        ]
    }
    
    # Add large game image if available
    if game.get('image'):
        embed_data["image"] = {"url": game['image']}
    
    payload = {
        "embeds": [embed_data]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        logger.info(f"Successfully notified: {game['title']}")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to send Discord notification for '{game['title']}': {e}")
        if hasattr(e.response, 'text'):
            logger.debug(f"Discord API response: {e.response.text}")
        return False


def _is_game_expired(end_timestamp: Optional[int]) -> bool:
    """
    Checks if a game's free promotion has expired.
    
    Args:
        end_timestamp: Unix timestamp of expiration
    
    Returns:
        bool: True if expired, False otherwise
    """
    if not end_timestamp:
        return False
    
    now_timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    return now_timestamp >= end_timestamp


def cleanup_expired_games(posted_games: Dict, current_games: List[Dict]) -> Dict:
    """
    Removes expired games from tracking to keep storage clean.
    
    Args:
        posted_games: Currently tracked games
        current_games: Games currently free on Epic Store
    
    Returns:
        Dict: Cleaned up tracked games
    """
    current_titles = {game['title'] for game in current_games}
    expired_titles = []
    
    for title, data in posted_games.items():
        if _is_game_expired(data.get('end_timestamp')) or title not in current_titles:
            expired_titles.append(title)
    
    for title in expired_titles:
        logger.info(f"Removing expired game from tracking: {title}")
        del posted_games[title]
    
    return posted_games


def main() -> None:
    """
    Main execution function that orchestrates the notification workflow.
    """
    logger.info("Starting Epic Games Freebie Notifier")
    
    if not validate_environment():
        logger.error("Configuration validation failed. Exiting.")
        sys.exit(1)
    
    try:
        free_games = get_free_games()
        
        if not free_games:
            logger.info("No free games found at this time")
            return
        
        posted_games = load_posted_games()
        
        for game in free_games:
            title = game["title"]
            end_timestamp = game["end_timestamp"]
            
            if title not in posted_games:
                logger.info(f"New free game detected: {title}")
                
                if send_discord_notification(game):
                    posted_games[title] = {
                        "end_timestamp": end_timestamp,
                        "notified_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
        
        posted_games = cleanup_expired_games(posted_games, free_games)
        
        save_posted_games(posted_games)
        
        logger.info("Completed notification check")
        
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

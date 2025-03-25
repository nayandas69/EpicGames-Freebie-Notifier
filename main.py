"""
 🫠 Epic Games Freebie Notifier ⏳

🔹 Author: nayandas69
🔹 GitHub: https://github.com/nayandas69/EpicGames-Freebie-Notifier
🔹 Description: This script automatically fetches free games from the Epic Games Store
   and sends a notification to a Discord channel via Webhook.
🔹 Features:
    1. Fetches free games from Epic Games API.
    2. Prevents duplicate postings using JSON storage.
    3. Displays game title, image, original price, and countdown timer.
    4. Sends rich Discord embeds with a "Claim Now" button.
"""

import datetime
import requests
import json
import os

# Load Discord Webhook from environment variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# JSON file to track already posted games
POSTED_FILE = "epics.json"

# Epic Games API URL for free games promotions
EPIC_GAMES_API = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
)


def get_free_games():
    """
    Fetches free games from the Epic Games Store API.

    Returns:
        list: A list of dictionaries, each containing game details like title, URL, image,
        original price, expiration timestamp, and remaining days.
    """
    response = requests.get(EPIC_GAMES_API)
    if response.status_code != 200:
        print("Failed to fetch game data")
        return []

    data = response.json()
    games = data["data"]["Catalog"]["searchStore"]["elements"]

    free_games = []
    for game in games:
        # Check if the game is free
        if game["price"]["totalPrice"]["discountPrice"] == 0:
            title = game["title"]
            url = f'https://store.epicgames.com/en-US/p/{game["productSlug"]}'
            image = game["keyImages"][0]["url"] if game["keyImages"] else ""
            original_price = game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
            end_timestamp = calculate_expiration_timestamp(game)
            remaining_days = calculate_remaining_days(end_timestamp)

            # Store game details in a list
            free_games.append(
                {
                    "title": title,
                    "url": url,
                    "image": image,
                    "original_price": original_price,
                    "end_timestamp": end_timestamp,
                    "remaining_days": remaining_days,
                }
            )

    return free_games


def calculate_expiration_timestamp(game):
    """
    Calculates the expiration timestamp for Discord countdown.

    Args:
        game (dict): The game data from the Epic Games API.

    Returns:
        int: Unix timestamp of the expiration date or None if unavailable.
    """
    try:
        end_date = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0][
            "endDate"
        ]
        end_datetime = datetime.datetime.fromisoformat(end_date[:-1])
        return int(end_datetime.timestamp())  # Convert to Unix timestamp
    except:
        return None  # If no valid expiration date, return None


def calculate_remaining_days(end_timestamp):
    """
    Calculates the remaining days until the game's free promotion expires.

    Args:
        end_timestamp (int): The expiration timestamp of the game.

    Returns:
        int: Number of remaining days, or None if expiration date is missing.
    """
    if not end_timestamp:
        return None
    now_timestamp = int(datetime.datetime.utcnow().timestamp())
    remaining_seconds = end_timestamp - now_timestamp
    return max(0, remaining_seconds // 86400)  # Convert seconds to days


def load_posted_games():
    """
    Loads previously posted game data to avoid duplicate notifications.

    Returns:
        dict: A dictionary containing previously posted games with their expiration timestamps.
    """
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return {}


def save_posted_games(posted):
    """
    Saves posted game data to a JSON file to prevent duplicate notifications.

    Args:
        posted (dict): Dictionary containing posted games.
    """
    with open(POSTED_FILE, "w") as f:
        json.dump(posted, f, indent=4)


def send_to_discord(game, status):
    """
    Sends a rich embed message to Discord with game details.

    Args:
        game (dict): The game details.
        status (str): "New" for a new free game, "Updated Expiration" for an update.
    """
    if game["end_timestamp"]:
        countdown = f"<t:{game['end_timestamp']}:R> (⏰ <t:{game['end_timestamp']}:t>)"
    else:
        countdown = "Unknown"

    embed = {
        "embeds": [
            {
                "title": f"{game['title']} ({status})",
                "description": (
                    f"🔥 **FREE for {game['remaining_days']} days!** ({countdown})\n\n"
                    f"💰 Original Price: ~~{game['original_price']}~~ → **FREE**\n\n"
                    f"👉 **[🎮 Claim Now]({game['url']})**"
                ),
                "color": 16776960,  # Yellow color
                "image": {"url": game["image"]},
                "footer": {
                    "text": "Epic Games Freebie Notifier",  # Footer (Not Clickable)
                    "icon_url": "https://avatars.githubusercontent.com/u/174907517?v=4",  # Icon (Optional)
                },
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK, json=embed)
    if response.status_code == 204:
        print(f"Successfully sent: {game['title']} ({status})")
    else:
        print(
            f"Failed to send: {game['title']} | {response.status_code} | {response.text}"
        )


def main():
    """
    Main function to fetch free games and send Discord notifications.
    """
    free_games = get_free_games()
    posted_games = load_posted_games()

    for game in free_games:
        title = game["title"]
        end_timestamp = game["end_timestamp"]
        remaining_days = game["remaining_days"]

        # Remove expired games
        if remaining_days == 0:
            if title in posted_games:
                print(f"{title} is no longer free. Removing from tracking.")
                del posted_games[title]
            continue

        # Send a notification for new games
        if title not in posted_games:
            send_to_discord(game, "New")
            posted_games[title] = {
                "end_timestamp": end_timestamp,
                "remaining_days": remaining_days,
            }

        # Send an update if the expiration date changes
        elif posted_games[title].get("remaining_days") != remaining_days:
            send_to_discord(game, "Updated Expiration")
            posted_games[title]["remaining_days"] = remaining_days

    # Save the updated list of posted games
    save_posted_games(posted_games)


if __name__ == "__main__":
    main()

import datetime
import requests
import json
import os

# Load Discord Webhook from environment variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
POSTED_FILE = "epics.json"

EPIC_GAMES_API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"


def get_free_games():
    """Fetches free games from Epic Games API."""
    response = requests.get(EPIC_GAMES_API)
    if response.status_code != 200:
        print("Failed to fetch game data")
        return []

    data = response.json()
    games = data["data"]["Catalog"]["searchStore"]["elements"]

    free_games = []
    for game in games:
        if game["price"]["totalPrice"]["discountPrice"] == 0:
            title = game["title"]
            url = f'https://store.epicgames.com/en-US/p/{game["productSlug"]}'
            image = game["keyImages"][0]["url"] if game["keyImages"] else ""
            original_price = game["price"]["totalPrice"]["fmtPrice"]["originalPrice"]
            end_timestamp = calculate_expiration_timestamp(game)

            free_games.append(
                {
                    "title": title,
                    "url": url,
                    "image": image,
                    "original_price": original_price,
                    "end_timestamp": end_timestamp,  # Store timestamp
                }
            )

    return free_games


def calculate_expiration_timestamp(game):
    """Calculates expiration timestamp for Discord countdown."""
    try:
        end_date = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["endDate"]
        end_datetime = datetime.datetime.fromisoformat(end_date[:-1])  # Convert to datetime object
        return int(end_datetime.timestamp())  # Convert to Unix timestamp
    except:
        return None  # If no valid expiration date, return None


def load_posted_games():
    """Loads previously posted game data."""
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return {}


def save_posted_games(posted):
    """Saves posted game data to avoid duplicate notifications."""
    with open(POSTED_FILE, "w") as f:
        json.dump(posted, f, indent=4)


def send_to_discord(game, status):
    """Sends a rich embed message to Discord."""
    if game["end_timestamp"]:
        countdown = f"<t:{game['end_timestamp']}:R> (⏰ <t:{game['end_timestamp']}:T>)"
    else:
        countdown = "Unknown"

    embed = {
        "embeds": [
            {
                "title": f"{game['title']} ({status})",
                "url": game["url"],
                "description": f"🔥 **FREE for {countdown}!**\n\n💰 Original Price: ~~{game['original_price']}~~ → **FREE**",
                "color": 16776960,  # Yellow color
                "image": {"url": game["image"]},
                "footer": {"text": "Epic Games Freebie Notifier"},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK, json=embed)
    if response.status_code == 204:
        print(f"Successfully sent: {game['title']} ({status})")
    else:
        print(f"Failed to send: {game['title']} | {response.status_code}")


def main():
    """Main function to fetch games and notify Discord."""
    free_games = get_free_games()
    posted_games = load_posted_games()

    for game in free_games:
        title = game["title"]
        end_timestamp = game["end_timestamp"]

        # Check if the game is expired
        if end_timestamp and end_timestamp < int(datetime.datetime.utcnow().timestamp()):
            posted_games[title] = {"status": "Expired"}
            continue  # Skip expired games

        # Check for new games
        if title not in posted_games:
            send_to_discord(game, "New")
            posted_games[title] = {"end_timestamp": end_timestamp}

        # Notify if expiration date has changed (any change)
        elif posted_games[title]["end_timestamp"] != end_timestamp:
            send_to_discord(game, "Updated Expiration")
            posted_games[title]["end_timestamp"] = end_timestamp  # Update expiration

    save_posted_games(posted_games)


if __name__ == "__main__":
    main()

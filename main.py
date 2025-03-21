import datetime
import requests
import json
import os

# Load Discord Webhook from environment variables
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
POSTED_FILE = "posted.json"

EPIC_GAMES_API = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
)


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
            free_days = calculate_remaining_days(game)

            free_games.append(
                {
                    "title": title,
                    "url": url,
                    "image": image,
                    "original_price": original_price,
                    "free_days": free_days,
                }
            )

    return free_games


def calculate_remaining_days(game):
    """Calculates remaining days until the offer expires."""
    try:
        end_date = game["promotions"]["promotionalOffers"][0]["promotionalOffers"][0][
            "endDate"
        ]
        remaining_days = (
            datetime.datetime.fromisoformat(end_date[:-1]) - datetime.datetime.utcnow()
        ).days
        return max(0, remaining_days)
    except:
        return "Unknown"


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


def send_to_discord(game):
    """Sends a rich embed message to Discord."""
    embed = {
        "embeds": [
            {
                "title": game["title"],
                "url": game["url"],
                "description": f"🔥 **FREE for {game['free_days']} more days!**\n\n💰 Original Price: ~~{game['original_price']}~~ → **FREE**",
                "color": 16776960,  # Yellow color
                "image": {"url": game["image"]},
                "footer": {"text": "Epic Games Freebie Notifier"},
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK, json=embed)
    if response.status_code == 204:
        print(f"✅ Successfully sent: {game['title']}")
    else:
        print(f"❌ Failed to send: {game['title']} | {response.status_code}")


def main():
    """Main function to fetch games and notify Discord."""
    free_games = get_free_games()
    posted_games = load_posted_games()

    for game in free_games:
        # Check if the game is expired
        if game["free_days"] == 0:
            posted_games[game["title"]] = {"status": "Expired"}
            continue  # Skip expired games

        # If the game is new, send a notification
        if game["title"] not in posted_games:
            send_to_discord(game)
            posted_games[game["title"]] = {
                "posted_date": str(datetime.date.today()),
                "expires_in_days": game["free_days"],
            }

        # Update the remaining days for already posted games
        elif posted_games[game["title"]].get("expires_in_days") not in [
            "Expired",
            None,
        ]:
            posted_games[game["title"]]["expires_in_days"] = game["free_days"]

    save_posted_games(posted_games)


if __name__ == "__main__":
    main()

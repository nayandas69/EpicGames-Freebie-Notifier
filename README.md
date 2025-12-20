# Epic Games Freebie Notifier

Get instant Discord notifications whenever Epic Games drops free games. No more missing out on freebies.

## What It Does

This script checks the Epic Games Store every hour and sends you a Discord notification when new free games are available. It keeps track of what it's already told you about, so you won't get spammed with duplicate notifications.

## Quick Start

**Don't want to set this up yourself?** Just join my Discord server and get notifications automatically: https://discord.gg/u9XfHZN8K9

### If You Want to Run It Yourself

1. **Get the code**
   ```bash
   git clone https://github.com/nayandas69/EpicGames-Freebie-Notifier.git
   cd EpicGames-Freebie-Notifier
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Discord webhook**
   - Go to your Discord server settings
   - Navigate to Integrations → Webhooks
   - Create a new webhook and copy the URL
   - Create a `.env` file and add:
     ```
     DISCORD_WEBHOOK=your_webhook_url_here
     ```

4. **Run it**
   ```bash
   python main.py
   ```

### Using GitHub Actions (Recommended)

The repo includes a GitHub Actions workflow that runs automatically every hour. Just fork the repo and add your Discord webhook URL as a repository secret named `DISCORD_WEBHOOK`. That's it.

## What You Get

When a new free game drops, you'll get a nice Discord message with:
- Game title and image
- Original price
- How long it's free for
- Direct link to claim it

## Epic Games API

This project fetches free games from the Epic Games API:

**API Endpoint:**
```bash
https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions
```

**Data Extracted:**
- `title`: Game name
- `productSlug`: Game URL
- `price`: Original & discount price
- `endDate`: Offer expiration time

**Official API Docs** 📄: [Epic Games API Documentation](https://dev.epicgames.com/docs/)

## License

MIT License - do whatever you want with it.

---

Made by [nayandas69](https://github.com/nayandas69)
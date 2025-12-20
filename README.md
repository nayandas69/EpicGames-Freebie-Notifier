# Epic Games Freebie Notifier

Get instant Discord notifications whenever Epic Games drops free games. No more missing out on freebies.

## What It Does

This script checks the Epic Games Store every hour and sends you a Discord notification when new free games are available. It keeps track of what it's already told you about, so you won't get spammed with duplicate notifications.

## Quick Start

**Don't want to set this up yourself?** Just join my [Discord server](https://discord.gg/u9XfHZN8K9) and get notifications automatically.

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

The repo includes a GitHub Actions workflow that runs automatically every hour. Just fork the repo and:

1. **Add Discord Webhook Secret**
   - Go to your repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `DISCORD_WEBHOOK`
   - Value: Your Discord webhook URL
   - Click "Add secret"

2. **Add Personal Access Token (PAT_TOKEN)** _(Required to commit as yourself)_
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name like "Epic Games Notifier"
   - Select these scopes:
     - [x] **public_repo** (under repo section)
     - [x] **workflow**
   - Generate and copy the token
   - Go to your repository Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `PAT_TOKEN`
   - Value: Your personal access token
   - Click "Add secret"

That's it! The workflow will run automatically and commits will appear as you.

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
![Profile Views](https://komarev.com/ghpvc/?username=nayandas69)

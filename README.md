# Epic Games Discord Bot

A production-ready Discord bot that tracks and notifies users about free games on the Epic Games Store.

## Features

- **🎮 Free Game Tracking**: Automatically monitors Epic Games Store for free games
- **📢 Smart Notifications**: Sends notifications only for new free games
- **⚙️ Configurable Settings**: Set notification times and channels per server
- **🎨 Rich Embeds**: Beautiful game displays with images, descriptions, and countdown timers
- **📊 Health Monitoring**: Built-in health checks and error logging
- **🔄 Caching**: Efficient API usage with intelligent caching
- **🐳 Docker Support**: Easy deployment with Docker and Docker Compose

## Commands

- `/freegames` - Display current free games on Epic Games Store
- `/configure notification_time HH:MM` - Set daily notification time (24-hour format)
- `/configure channel #channel` - Set notification channel

## Quick Start

### Prerequisites

- Python 3.9+
- Discord Bot Token
- Discord Server with appropriate permissions

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nayandas69/EpicGames-Freebie-Notifier.git
   cd EpicGames-Freebie-Notifier
   ```

2. **Run setup script**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Discord bot token and settings
   ```

4. **Run the bot**
   ```bash
   ./scripts/run.sh
   ```

### Docker Deployment

1. **Using Docker Compose (Recommended)**
   ```bash
   # Copy and configure environment
   cp .env.example .env
   # Edit .env with your settings
   
   # Start the bot
   docker-compose up -d
   
   # View logs
   docker-compose logs -f epic-games-bot
   ```

2. **Using Docker directly**
   ```bash
   # Build image
   docker build -t epic-games-bot .
   
   # Run container
   docker run -d \
     --name epic-games-bot \
     --env-file .env \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     epic-games-bot
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Discord bot token | - | ✅ |
| `DISCORD_GUILD_ID` | Guild ID for command syncing | - | ❌ |
| `NOTIFICATION_CHANNEL_ID` | Default notification channel | - | ❌ |
| `NOTIFICATION_TIME` | Default notification time (HH:MM) | `13:00` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `EPIC_GAMES_REGION` | Epic Games region | `US` | ❌ |
| `DATABASE_PATH` | SQLite database path | `./data/bot.db` | ❌ |

### Discord Bot Setup

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Go to "Bot" section
   - Create bot and copy token

2. **Bot Permissions**
   Required permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History

3. **Invite Bot to Server**
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=274877908992&scope=bot%20applications.commands
   ```


### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_epic_games_service.py
```

### Code Quality

```bash
# Linting
flake8 src tests

# Type checking
mypy src

# Code formatting
black src tests
```

## Monitoring

### Health Checks

The bot includes built-in health monitoring:

- **Database Health**: Monitors database connectivity
- **API Health**: Tracks Epic Games API availability
- **Bot Status**: Logs bot operational status

### Metrics (Optional)

Enable monitoring with Prometheus and Grafana:

```bash
# Start with monitoring
docker-compose --profile monitoring up -d

# Access Grafana at http://localhost:3000
# Username: admin, Password: admin
```

## API Rate Limiting

The bot implements intelligent rate limiting:

- **Caching**: API responses cached for 1 hour
- **Batch Processing**: Efficient notification handling
- **Error Handling**: Graceful degradation on API failures

## Database Schema

### Tables

- **guild_settings**: Server-specific configuration
- **notified_games**: Tracks notified games per server
- **bot_health**: Health monitoring logs

## Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Check bot permissions in Discord server
   - Verify bot token in .env file
   - Check bot is online in Discord

2. **No notifications being sent**
   - Verify notification channel is set: `/configure channel #your-channel`
   - Check notification time: `/configure notification_time 13:00`
   - Ensure bot has permission to send messages in notification channel

3. **Database errors**
   - Check data directory permissions
   - Verify DATABASE_PATH in .env
   - Check disk space

### Logs

```bash
# View bot logs
tail -f logs/bot.log

# Docker logs
docker-compose logs -f epic-games-bot
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests before committing
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/nayandas69/EpicGames-Freebie-Notifier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nayandas69/EpicGames-Freebie-Notifier/discussions)

## Acknowledgments

- Epic Games Store for providing free games
- Discord.py community for excellent documentation
- Contributors and testers


> \[!CAUTION] 
> This bot is not affiliated with Epic Games. It uses publicly available APIs to track free game promotions.
# Twitch Bot

A production-ready Twitch bot built with Python and the twitchio library.

## Features

- OAuth authentication flow for secure token management
- Real-time chat connection and command handling
- Basic commands: !hello, !uptime
- Automatic reconnection logic
- Comprehensive logging and error handling
- Configuration management for easy deployment

## Project Structure

```
twitch_bot/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py        # Configuration management
├── src/
│   ├── __init__.py
│   ├── bot.py            # Main bot class
│   ├── commands/         # Command handlers
│   │   ├── __init__.py
│   │   ├── base.py       # Base command class
│   │   └── basic.py      # Basic commands (!hello, !uptime)
│   ├── auth/             # Authentication
│   │   ├── __init__.py
│   │   └── oauth.py      # OAuth flow implementation
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   └── logger.py     # Logging configuration
│   └── exceptions/       # Custom exceptions
│       ├── __init__.py
│       └── bot_exceptions.py
├── tests/                # Test files
│   ├── __init__.py
│   ├── test_bot.py
│   └── test_commands.py
├── .env.example          # Environment variables template
└── main.py              # Entry point
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

All configuration is managed through environment variables. See `.env.example` for required settings.

## Security Notes

- Never commit your actual tokens or secrets
- Use environment variables for all sensitive data
- The OAuth flow handles token refresh automatically
- Tokens are stored securely in the local environment

## Commands

- `!hello` - Greets the user
- `!uptime` - Shows bot uptime

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request
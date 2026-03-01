# Twitch Bot Setup Guide

This guide will walk you through setting up your Twitch bot from start to finish.

## Prerequisites

- Python 3.8 or higher
- A Twitch account (for your bot)
- Access to the Twitch Developer Console

## Step 1: Create a Twitch Application

1. **Go to [Twitch Developer Console](https://dev.twitch.tv/console/apps)**
2. **Log in with your Twitch account**
3. **Click "Register Your Application"**
4. **Fill out the application details:**
   - **Name**: Choose a name for your bot (e.g., "My Twitch Bot")
   - **OAuth Redirect URLs**: Add `http://localhost:8080` (or your preferred URL)
   - **Category**: Select "Chat Bot"
5. **Click "Create"**
6. **Copy your Client ID and Client Secret** - you'll need these!

## Step 2: Set Up Your Bot Account

1. **Create a new Twitch account** for your bot (if you don't have one already)
2. **Note down the username** - this will be your bot's name
3. **Make sure to verify the email** associated with this account

## Step 3: Install Dependencies

1. **Navigate to the project directory:**
   ```bash
   cd twitch_bot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Configure Your Bot

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual credentials:
   ```bash
   # Edit .env file with your text editor of choice
   nano .env  # or vim, code, etc.
   ```

3. **Fill in your credentials:**
   ```env
   # Your Twitch application credentials (from Step 1)
   TWITCH_CLIENT_ID=your_actual_client_id_here
   TWITCH_CLIENT_SECRET=your_actual_client_secret_here
   
   # Your bot account details (from Step 2)
   TWITCH_BOT_USERNAME=your_bot_username
   TWITCH_CHANNEL_NAME=channel_you_want_to_join
   
   # Optional settings (can keep defaults)
   COMMAND_PREFIX=!
   MAX_RECONNECT_ATTEMPTS=5
   RECONNECT_DELAY=30
   LOG_LEVEL=INFO
   ```

## Step 5: Test Your Configuration

1. **Run the configuration test:**
   ```bash
   python -c "
   from config.settings import Config, ConfigurationError
   try:
       config = Config.from_env()
       config.validate()
       print('✅ Configuration is valid!')
   except ConfigurationError as e:
       print(f'❌ Configuration error: {e}')
   except Exception as e:
       print(f'❌ Error loading configuration: {e}')
   "
   ```

2. **Check that all required fields are filled:**
   - `TWITCH_CLIENT_ID` should not be empty
   - `TWITCH_CLIENT_SECRET` should not be empty  
   - `TWITCH_BOT_USERNAME` should not be empty
   - `TWITCH_CHANNEL_NAME` should not be empty

## Step 6: Run the Bot

1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Expected output** should look something like:
   ```
   2024-01-15 14:30:00 - twitch_bot - INFO - Loading bot configuration...
   2024-01-15 14:30:00 - twitch_bot - INFO - Initializing Twitch bot...
   2024-01-15 14:30:00 - twitch_bot - INFO - Starting Twitch bot...
   2024-01-15 14:30:00 - twitch_bot - INFO - Bot 'YourBotName' is ready!
   2024-01-15 14:30:00 - twitch_bot - INFO - Connected to channels: ['yourchannel']
   ```

3. **If you see errors**, check the troubleshooting section below.

## Step 7: Test Bot Commands

Once your bot is running and connected:

1. **Join the channel** you configured (or have someone else join)
2. **Try these commands in chat:**
   - `!hello` - Should greet you
   - `!uptime` - Should show bot uptime  
   - `!ping` - Should respond with "pong"
   - `!help` - Should show available commands
   - `!about` - Should show bot information

3. **Expected responses:**
   ```
   User: !hello
   Bot: Hello YourUsername! 👋
   
   User: !uptime  
   Bot: Bot has been running for 2m 30s 🕐
   
   User: !ping
   Bot: pong! 🏓
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Configuration error" or missing credentials
**Problem**: Your `.env` file is missing required values.

**Solution**: 
- Double-check that your `.env` file has all the required fields filled in
- Make sure there are no extra spaces around the `=` signs
- Verify your Twitch application credentials from the developer console

#### 2. "Authentication failed" or connection errors
**Problem**: Invalid Twitch credentials or permissions.

**Solution**:
- Verify your Client ID and Client Secret are correct
- Make sure your bot account exists and is verified
- Check that the channel name you want to join actually exists

#### 3. "Module not found" errors
**Problem**: Dependencies aren't installed or Python path issues.

**Solution**:
- Make sure you're in the correct directory
- Activate your virtual environment if you created one
- Reinstall dependencies: `pip install -r requirements.txt`

#### 4. Bot connects but doesn't respond to commands
**Problem**: Command prefix mismatch or channel not joined.

**Solution**:
- Check that you're using the correct command prefix (default `!`)
- Verify the bot actually joined your channel in Twitch chat
- Look for connection messages in the logs

#### 5. Bot disconnects frequently
**Problem**: Network issues or rate limiting.

**Solution**:
- Check your internet connection stability
- Review the log files for specific error messages
- The bot has automatic reconnection logic - let it retry

### Getting Help

1. **Check the logs**: Look in `logs/bot.log` for detailed error messages
2. **Enable debug logging**: Set `LOG_LEVEL=DEBUG` in your `.env` file
3. **Test OAuth flow**: If using advanced features, test the OAuth URL generation

## Security Best Practices

### Token Management
- **Never commit your `.env` file** to version control
- **Use environment variables** in production deployments  
- **Rotate your client secret** periodically through the Twitch console
- **Use least privilege**: Only request the scopes your bot actually needs

### Production Deployment
- Use a proper process manager (systemd, PM2, etc.)
- Set up log rotation to prevent disk space issues
- Monitor your bot's connection status and uptime
- Consider using a reverse proxy if exposing web endpoints

### OAuth Security (Advanced)
If implementing user authentication features:
- Store refresh tokens securely (encrypted at rest)
- Implement proper token expiration handling
- Use HTTPS for all OAuth redirects in production
- Validate state parameters to prevent CSRF attacks

## Next Steps

Once your bot is working:

1. **Customize commands** - Add your own commands in `src/commands/`
2. **Add features** - Implement moderation, game integration, etc.
3. **Deploy to production** - Set up proper hosting and monitoring
4. **Monitor performance** - Track uptime, command usage, errors

## File Structure Reference

After setup, your project should look like this:
```
twitch_bot/
├── .env                    # Your actual credentials (not in git)
├── .env.example           # Template for others
├── main.py               # Entry point
├── requirements.txt      # Dependencies  
├── config/              # Configuration management
│   ├── __init__.py
│   └── settings.py
├── src/                 # Source code
│   ├── __init__.py
│   ├── bot.py          # Main bot class
│   ├── auth/           # OAuth handling
│   ├── commands/       # Command handlers
│   ├── utils/          # Utilities
│   └── exceptions/     # Custom errors
├── tests/              # Test files
└── logs/               # Log files (created automatically)
```

Your bot is now ready to join Twitch chats and respond to commands! 🎉
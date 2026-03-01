"""
Main entry point for the Twitch bot.
"""

import asyncio
import sys
import signal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot import TwitchBot
from config.settings import Config, ConfigurationError
from src.utils.logger import setup_logger


async def main():
    """Main application entry point."""
    
    # Set up logging
    logger = setup_logger(
        name="twitch_bot",
        level="INFO"
    )
    # Also surface TwitchIO's internal logger so errors aren't swallowed
    setup_logger(name="twitchio", level="INFO")
    
    try:
        # Load and validate configuration
        logger.info("Loading bot configuration...")
        config = Config.from_env()
        config.validate()
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Create and start the bot
    logger.info("Initializing Twitch bot...")
    
    try:
        # Create bot instance
        bot = TwitchBot(config)
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(bot.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot with retry logic
        logger.info("Starting Twitch bot...")
        await bot.start_with_retry()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed with error: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot application terminated")


if __name__ == "__main__":
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Run the main application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Application failed: {e}")
        sys.exit(1)
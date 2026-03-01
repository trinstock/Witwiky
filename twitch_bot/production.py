"""
Production deployment script for the Twitch bot.
"""

import os
import sys
import signal
import asyncio
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.bot import TwitchBot
from config.settings import Config, ConfigurationError
from src.utils.logger import setup_logger


class ProductionBot(TwitchBot):
    """Production-ready Twitch bot with enhanced monitoring."""
    
    def __init__(self, config: "Config"):
        super().__init__(config)
        
        # Production-specific settings
        self.health_check_port = int(os.getenv("HEALTH_CHECK_PORT", "8080"))
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "false").lower() == "true"
        
        # Performance tracking
        self.command_stats = {}
        self.start_time = None
        
    async def start_with_retry(self) -> None:
        """Start the bot with production-grade error handling."""
        
        # Set up health check endpoint
        if self.health_check_port:
            asyncio.create_task(self._start_health_server())
        
        try:
            await super().start_with_retry()
            
        except Exception as e:
            self.logger.error(f"Production bot failed: {e}")
            raise
        finally:
            # Cleanup on shutdown
            if hasattr(self, 'health_server'):
                self.health_server.close()
    
    async def _start_health_server(self):
        """Start a simple health check HTTP server."""
        try:
            from aiohttp import web, ClientTimeout
            
            async def health_check(request):
                """Health check endpoint."""
                return web.json_response({
                    "status": "healthy",
                    "uptime_seconds": int(asyncio.get_event_loop().time() - self.start_time) if self.start_time else 0,
                    "connected_channels": len(self.connected_channels),
                    "commands_registered": len(self.command_handler.commands)
                })
            
            async def metrics_endpoint(request):
                """Metrics endpoint for monitoring."""
                if not self.metrics_enabled:
                    return web.json_response({"error": "metrics disabled"}, status=403)
                
                # Collect basic metrics
                return web.json_response({
                    "uptime_seconds": int(asyncio.get_event_loop().time() - self.start_time) if self.start_time else 0,
                    "connected_channels": len(self.connected_channels),
                    "command_stats": self.command_stats
                })
            
            app = web.Application()
            app.router.add_get('/health', health_check)
            app.router.add_get('/metrics', metrics_endpoint)
            
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', self.health_check_port)
            await site.start()
            
            self.logger.info(f"Health check server started on port {self.health_check_port}")
            
        except ImportError:
            self.logger.warning("aiohttp not available, health check server disabled")
        except Exception as e:
            self.logger.error(f"Failed to start health check server: {e}")
    
    async def _handle_message(self, message):
        """Enhanced message handling with metrics."""
        
        # Track command usage
        content = message.content.strip()
        command = self.command_handler.get_command(content)
        
        if command:
            # Update command statistics
            cmd_name = command.name
            self.command_stats[cmd_name] = self.command_stats.get(cmd_name, 0) + 1
        
        # Call parent implementation
        await super()._handle_message(message)


async def main():
    """Production deployment entry point."""
    
    # Set up production logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE")  # Optional file logging
    
    logger = setup_logger(
        name="twitch_bot",
        level=log_level,
        log_file=log_file
    )
    
    logger.info("Starting Twitch bot in production mode...")
    
    try:
        # Load and validate configuration
        config = Config.from_env()
        config.validate()
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Create production bot
    try:
        bot = ProductionBot(config)
        
        # Set up graceful shutdown handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(bot.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the bot
        await bot.start_with_retry()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Production bot failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Production bot terminated")


if __name__ == "__main__":
    # Ensure required directories exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Run production application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Production application failed: {e}")
        sys.exit(1)
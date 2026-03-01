"""
Modified Twitch bot that bypasses TwitchIO's API parameter bug.
"""

import asyncio
import time
from typing import Dict, Any

from twitchio.ext import commands as TwitchCommands
from .api.custom_wrapper import CustomTwitchAPI
from .auth.oauth import OAuthManager
from .commands.base import CommandHandler, BaseCommand
from config.settings import Config
from .utils.logger import get_logger


class ModifiedTwitchBot(TwitchCommands.Bot):
    """Modified Twitch bot that uses custom API wrapper."""
    
    def __init__(self, config: "Config"):
        """Initialize the modified Twitch bot.
        
        Args:
            config: Bot configuration instance
        """
        self.config = config
        self.logger = get_logger("twitch_bot")
        
        # Initialize OAuth manager for token management
        self.oauth_manager = OAuthManager(
            client_id=config.twitch.client_id,
            client_secret=config.twitch.client_secret
        )
        
        # Get proper OAuth token using client credentials
        oauth_token = self.oauth_manager.get_app_token()
        
        # Initialize custom API wrapper
        self.api_wrapper = CustomTwitchAPI(
            client_id=config.twitch.client_id,
            access_token=oauth_token
        )
        
        # Initialize base twitchio bot (skipping user validation)
        super().__init__(
            client_id=config.twitch.client_id,
            client_secret=config.twitch.client_secret,
            bot_id="test_bot",  # Use generic name to avoid validation
            prefix=config.bot.command_prefix
        )
        
        # Command handling
        self.command_handler = CommandHandler(command_prefix=config.bot.command_prefix)
        self._setup_commands()
        
        # Connection management
        self.start_time = time.time()
        self.reconnect_attempts = 0
        self.is_shutting_down = False
        
        # State tracking
        self.connected_channels: Dict[str, Any] = {}
        
    def _setup_commands(self) -> None:
        """Set up basic commands."""
        from .commands.basic import get_basic_commands
        
        # Get basic commands
        basic_commands = get_basic_commands()
        
        # Configure help command with our handler
        for cmd in basic_commands:
            if hasattr(cmd, 'command_handler'):
                cmd.command_handler = self.command_handler
                
        # Register commands with our handler
        for command in basic_commands:
            self.command_handler.register_command(command)
    
    async def event_ready(self):
        """Called when the bot is ready and connected to Twitch."""
        self.logger.info(f"Modified Bot '{self.bot_id}' is ready!")
        
        # Reset reconnect attempts on successful connection
        self.reconnect_attempts = 0
        
        # Join the target channel using custom API validation
        await self._join_target_channel()
    
    async def _join_target_channel(self):
        """Join the target channel using custom API validation."""
        try:
            # Use our custom wrapper to validate and get user info
            target_user = await self.api_wrapper.get_user_by_login(self.config.twitch.channel_name)
            
            if target_user:
                self.logger.info(f"Successfully validated channel: {target_user['login']}")
                
                # Join the channel using TwitchIO's join method
                channel = self.get_channel(target_user['login'])
                if not channel:
                    # If no existing channel object, create one
                    await self.join_channels([target_user['login']])
                
                # Send initial message
                channel = self.get_channel(target_user['login'])
                if channel:
                    await channel.send(f"🤖 Modified bot is online! Type {self.config.bot.command_prefix}help for commands.")
                    self.logger.info(f"Bot successfully joined channel: {target_user['login']}")
            else:
                self.logger.error(f"Channel '{self.config.twitch.channel_name}' not found on Twitch")
                
        except Exception as e:
            self.logger.error(f"Failed to join channel: {e}")
    
    async def event_message(self, message):
        """Called when a message is received."""
        try:
            # Ignore messages from the bot itself
            if message.echo:
                return
                
            # Process commands using our custom handler
            await self._handle_message(message)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _handle_message(self, message):
        """Handle incoming messages and process commands."""
        try:
            content = message.content.strip()
            command = self.command_handler.get_command(content)

            if command:
                response = await self.command_handler.execute_command(
                    message=message,
                    command=command,
                    user=message.author.name if hasattr(message, 'author') else "Unknown",
                    channel=message.channel.name if hasattr(message, 'channel') and hasattr(message.channel, 'name') else "Unknown"
                )
                if response:
                    await message.channel.send(response)
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
    
    async def event_channel_joined(self, channel):
        """Called when the bot joins a channel."""
        self.logger.info(f"Successfully joined channel: {channel.name}")
        self.connected_channels[channel.name] = channel
        
    async def event_connect(self):
        """Called when the bot successfully connects to Twitch."""
        self.logger.info("Modified Bot connected to Twitch IRC")
        
    async def event_disconnect(self):
        """Called when the bot disconnects from Twitch."""
        self.logger.warning("Modified Bot disconnected from Twitch")
        
    async def event_reconnect(self):
        """Called when the bot is attempting to reconnect."""
        self.logger.info("Modified Bot attempting to reconnect...")
        
    async def start_with_retry(self) -> None:
        """Start the bot with automatic reconnection logic."""
        while not self.is_shutting_down and self.reconnect_attempts < self.config.bot.max_reconnect_attempts:
            try:
                await self.start()
                
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt, shutting down...")
                await self.shutdown()
                
            except Exception as e:
                self.reconnect_attempts += 1
                error_msg = f"Connection failed (attempt {self.reconnect_attempts}/{self.config.bot.max_reconnect_attempts}): {e}"
                self.logger.error(error_msg)
                
                if self.reconnect_attempts < self.config.bot.max_reconnect_attempts:
                    wait_time = self.config.bot.reconnect_delay * (2 ** (self.reconnect_attempts - 1))  # Exponential backoff
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error("Max reconnection attempts reached. Shutting down.")
                    raise ConnectionError(f"Failed to connect after {self.reconnect_attempts} attempts")
    
    async def shutdown(self) -> None:
        """Gracefully shut down the bot."""
        self.is_shutting_down = True
        self.logger.info("Shutting down modified bot...")
        
        try:
            # Close all channels
            for channel_name, channel in self.connected_channels.items():
                try:
                    await channel.send("🤖 Modified bot is going offline. Goodbye!")
                except Exception as e:
                    self.logger.error(f"Error sending shutdown message to {channel_name}: {e}")
            
            # Close the bot connection
            await self.close()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        
        finally:
            self.logger.info("Modified bot shutdown complete")
    
    def get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # Calculate days, hours, minutes, seconds
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        # Format the uptime string
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def add_command(self, command: BaseCommand) -> None:
        """Add a new command to the bot."""
        self.command_handler.register_command(command)
        
    def get_commands(self) -> Dict[str, BaseCommand]:
        """Get all registered commands."""
        return self.command_handler.get_all_commands()
    
    async def send_message(self, channel_name: str, message: str) -> bool:
        """Send a message to a specific channel."""
        try:
            channel = self.get_channel(channel_name)
            if channel:
                await channel.send(message)
                return True
            else:
                self.logger.warning(f"Channel {channel_name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to send message to {channel_name}: {e}")
            return False
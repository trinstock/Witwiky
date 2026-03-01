"""
Main Twitch bot class with connection handling and command processing.
"""

import asyncio
import time
import requests
from typing import Optional, Dict, Any

try:
    from twitchio.ext import commands
    from twitchio.eventsub import ChatMessageSubscription
    from twitchio.web import AiohttpAdapter
except ImportError:
    # Fallback for development/testing without full twitchio installation
    class MockBot:
        def __init__(self, *args, **kwargs):
            pass
        async def start(self): pass

    commands = type('commands', (), {'Bot': MockBot})()

from .auth.oauth import OAuthManager
from .commands.base import CommandHandler, BaseCommand
from .exceptions.bot_exceptions import (
    ConnectionError,
    AuthenticationError,
    ConfigurationError
)
from .utils.logger import get_logger


class TwitchBot(commands.Bot):
    """Main Twitch bot class built for TwitchIO v3 (EventSub WebSocket)."""

    def __init__(self, config: "Config"):
        """Initialize the Twitch bot.

        Args:
            config: Bot configuration instance
        """
        self.config = config
        self.logger = get_logger("twitch_bot")

        # Initialize OAuth manager and get app token
        self.oauth_manager = OAuthManager(
            client_id=config.twitch.client_id,
            client_secret=config.twitch.client_secret
        )
        oauth_token = self.oauth_manager.get_app_token()

        # TwitchIO v3 requires bot_id to be the numeric Twitch user ID
        bot_user_id = self._fetch_user_id(
            login=config.twitch.bot_username,
            access_token=oauth_token,
            client_id=config.twitch.client_id
        )

        # Pre-fetch broadcaster IDs for all configured channels
        self._broadcaster_ids: dict = {}
        for channel in config.twitch.channel_names:
            self._broadcaster_ids[channel] = self._fetch_user_id(
                login=channel,
                access_token=oauth_token,
                client_id=config.twitch.client_id
            )

        # Keep first channel's ID for backward compat
        self._broadcaster_id = self._broadcaster_ids.get(config.twitch.channel_name, "")

        # Initialize base twitchio bot (v3 API)
        super().__init__(
            client_id=config.twitch.client_id,
            client_secret=config.twitch.client_secret,
            bot_id=bot_user_id,
            prefix=config.bot.command_prefix
        )

        # Command handling
        self.command_handler = CommandHandler(command_prefix=config.bot.command_prefix)
        self._setup_commands()

        # Connection management
        self.start_time = time.time()
        self.reconnect_attempts = 0
        self.is_shutting_down = False

    def _get_user_token(self) -> Optional[str]:
        """Return the current user access token string, or None if unavailable."""
        token_obj = self.tokens.get(self.bot_id)
        if token_obj is None:
            return None
        return getattr(token_obj, "access_token", None)

    @staticmethod
    def _fetch_user_id(login: str, access_token: str, client_id: str) -> str:
        """Fetch the numeric Twitch user ID for a given username.

        TwitchIO v3 requires bot_id to be the numeric user ID, not the username.

        Raises:
            ConfigurationError: If the username is not found on Twitch
        """
        response = requests.get(
            "https://api.twitch.tv/helix/users",
            params={"login": login},
            headers={
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()
        users = response.json().get("data", [])
        if not users:
            raise ConfigurationError(f"Twitch user '{login}' not found")
        return users[0]["id"]

    def _setup_commands(self) -> None:
        """Register basic bot commands."""
        from .commands.basic import get_basic_commands

        basic_commands = get_basic_commands()

        for cmd in basic_commands:
            if hasattr(cmd, 'command_handler') and cmd.command_handler is None:
                cmd.command_handler = self.command_handler
            if hasattr(cmd, 'broadcaster_id') and cmd.broadcaster_id is None:
                cmd.client_id = self.config.twitch.client_id
                cmd.broadcaster_id = self._broadcaster_id
                cmd.get_token = self._get_user_token
            if hasattr(cmd, 'bot_id') and cmd.bot_id is None:
                cmd.bot_id = self.bot_id

        for command in basic_commands:
            self.command_handler.register_command(command)

    async def setup_hook(self) -> None:
        """Called after login. Sets up OAuth adapter and subscribes to chat."""
        # Start the aiohttp adapter for OAuth token management.
        # On first run, the user must visit the OAuth URL below to authorize.
        # The token is then saved to .tio.tokens.json and loaded automatically
        # on all subsequent runs.
        await self.set_adapter(AiohttpAdapter(port=8080))

        if self.bot_id in self.tokens:
            # Token already loaded from .tio.tokens.json — subscribe immediately
            await self._subscribe_to_chat()
        else:
            self.logger.warning(
                "\n"
                + "=" * 60 + "\n"
                "FIRST-TIME SETUP REQUIRED\n"
                "The bot needs a user access token to read chat.\n\n"
                "Steps:\n"
                "  1. Make sure http://localhost:8080/oauth/callback is\n"
                "     registered as a redirect URI in your Twitch app at\n"
                "     https://dev.twitch.tv/console/apps\n\n"
                "  2. Visit this URL in your browser while the bot is running:\n"
                "     http://localhost:8080/oauth?scopes=user:read:chat+user:write:chat+user:bot+clips:edit+moderator:manage:banned_users\n\n"
                "  3. Log in as your BOT account and authorize.\n"
                "  4. The bot will connect to chat automatically.\n"
                + "=" * 60
            )

    async def _subscribe_to_chat(self) -> None:
        """Subscribe to chat messages via EventSub WebSocket."""
        # Clean up any stale subscriptions from previous sessions that weren't
        # gracefully closed (they keep pointing at dead WebSocket sessions).
        try:
            await self.delete_all_eventsub_subscriptions()
            self.logger.info("Cleared stale EventSub subscriptions.")
        except Exception as e:
            self.logger.warning(f"Could not clear stale subscriptions: {e}")

        for channel, broadcaster_id in self._broadcaster_ids.items():
            await self.subscribe_websocket(
                ChatMessageSubscription(
                    broadcaster_user_id=broadcaster_id,
                    user_id=self.bot_id
                )
            )

        channels = ", ".join(f"#{c}" for c in self._broadcaster_ids)
        self.logger.info(f"Bot is ready and listening in {channels}")

    async def add_token(self, token: str, refresh: str):
        """Add a token and immediately persist it so it survives restarts."""
        result = await super().add_token(token, refresh)
        await self.save_tokens()
        return result

    async def event_oauth_authorized(self, payload) -> None:
        """Called when the bot user successfully authorizes via OAuth."""
        await super().event_oauth_authorized(payload)

        self.logger.info(
            f"OAuth authorization successful!\n"
            f"  Authorized user : {payload.user_login} (id={payload.user_id})\n"
            f"  Scopes granted  : {payload.scope}\n"
            f"  Expected bot_id : {self.bot_id}"
        )

        if payload.user_id != self.bot_id:
            self.logger.error(
                f"Wrong account authorized! Expected bot '{self.config.twitch.bot_username}' (id={self.bot_id}) "
                f"but got '{payload.user_login}' (id={payload.user_id}). "
                f"Please log out of Twitch in your browser and re-authorize as the bot account."
            )
            return

        self.logger.info("Connecting to chat...")
        try:
            await self._subscribe_to_chat()
        except Exception as e:
            self.logger.error(f"Failed to subscribe to chat after OAuth: {e}")

    async def event_error(self, payload) -> None:
        """Surface TwitchIO internal errors through our logger."""
        self.logger.error(
            f"TwitchIO error in '{payload.listener.__qualname__}': {payload.error}",
            exc_info=payload.error
        )

    async def event_message(self, payload) -> None:
        """Called when a chat message is received (TwitchIO v3 ChatMessage)."""
        try:
            await self._handle_message(payload)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def _handle_message(self, payload) -> None:
        """Handle an incoming chat message and dispatch commands.

        Args:
            payload: TwitchIO v3 ChatMessage object
        """
        content = payload.text.strip()
        command = self.command_handler.get_command(content)

        if command:
            try:
                response = await self.command_handler.execute_command(
                    message=payload,
                    command=command,
                    user=payload.chatter.name,
                    channel=payload.broadcaster.name,
                    broadcaster_id=payload.broadcaster.id
                )

                if response:
                    await payload.respond(response)

            except Exception as e:
                self.logger.error(f"Command execution failed: {e}")
                try:
                    await payload.respond(
                        f"Sorry {payload.chatter.name}, there was an error executing that command."
                    )
                except Exception:
                    pass

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
                error_msg = (
                    f"Connection failed "
                    f"(attempt {self.reconnect_attempts}/{self.config.bot.max_reconnect_attempts}): {e}"
                )
                self.logger.error(error_msg)

                if self.reconnect_attempts < self.config.bot.max_reconnect_attempts:
                    wait_time = self.config.bot.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
                    self.logger.info(f"Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error("Max reconnection attempts reached. Shutting down.")
                    raise ConnectionError(f"Failed to connect after {self.reconnect_attempts} attempts")

    async def shutdown(self) -> None:
        """Gracefully shut down the bot."""
        self.is_shutting_down = True
        self.logger.info("Shutting down bot...")
        try:
            await self.close()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            self.logger.info("Bot shutdown complete")

    def get_uptime(self) -> str:
        """Get bot uptime as a formatted string."""
        uptime_seconds = int(time.time() - self.start_time)

        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

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
        """Send a message to a specific channel.

        Args:
            channel_name: Name of the channel
            message: Message to send

        Returns:
            True if successful, False otherwise
        """
        try:
            broadcaster = self.create_partialuser(
                user_id=self._broadcaster_id,
                user_login=channel_name
            )
            await broadcaster.send_message(message, sender=self.bot_id)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to {channel_name}: {e}")
            return False

"""
Basic commands for the Twitch bot.
"""

import time
from typing import Any, Optional

from .base import BaseCommand


class HelloCommand(BaseCommand):
    """Simple greeting command."""
    
    def __init__(self):
        super().__init__(
            name="hello",
            description="Greets the user with a friendly message"
        )
        
    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the hello command.
        
        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context
            
        Returns:
            Greeting response
        """
        # Get user information if available
        user = kwargs.get("user", "there")
        
        responses = [
            f"Hello {user}! 👋",
            f"Hey there, {user}! How's it going? 😊",
            f"Hi {user}! Welcome to the chat! 🎉",
            f"Greetings, {user}! Great to see you here! ✨"
        ]
        
        # Simple random selection (could be enhanced with proper randomness)
        import time
        response_index = int(time.time()) % len(responses)
        
        return responses[response_index]


class UptimeCommand(BaseCommand):
    """Shows bot uptime information."""
    
    def __init__(self, start_time: float = None):
        super().__init__(
            name="uptime",
            description="Shows how long the bot has been running"
        )
        self.start_time = start_time or time.time()
        
    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the uptime command.
        
        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context
            
        Returns:
            Uptime information string
        """
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # Calculate days, hours, minutes, seconds
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        # Format the uptime string
        if days > 0:
            uptime_str = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            uptime_str = f"{minutes}m {seconds}s"
        else:
            uptime_str = f"{seconds}s"
            
        return f"Bot has been running for {uptime_str} 🕐"


class HelpCommand(BaseCommand):
    """Shows help information about available commands."""
    
    def __init__(self, command_handler=None):
        super().__init__(
            name="help",
            description="Shows this help message"
        )
        self.command_handler = command_handler
        
    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the help command.
        
        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context
            
        Returns:
            Help text string
        """
        if self.command_handler:
            return self.command_handler.get_help_text()
        else:
            return "Available commands: !hello, !uptime"


class PingCommand(BaseCommand):
    """Simple ping/pong command for testing connectivity."""
    
    def __init__(self):
        super().__init__(
            name="ping",
            description="Responds with pong to test bot connectivity"
        )
        
    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the ping command.
        
        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context
            
        Returns:
            Pong response
        """
        return "pong! 🏓"


class AboutCommand(BaseCommand):
    """Shows information about the bot."""

    def __init__(self, version: str = "1.0.0"):
        super().__init__(
            name="about",
            description="Shows information about this bot"
        )
        self.version = version

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the about command.

        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context

        Returns:
            About information string
        """
        return (
            f"🤖 Twitch Bot v{self.version} | "
            f"Built with Python and twitchio | "
            f"Made with ❤️ for the Twitch community"
        )


class LurkCommand(BaseCommand):
    """Announce that a user is lurking."""

    def __init__(self):
        super().__init__(
            name="lurk",
            description="Let the streamer know you're lurking"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "Someone")
        return f"{user} is lurking in the shadows... 👀 Thanks for the support!"


class UnlurkCommand(BaseCommand):
    """Announce that a user has returned from lurking."""

    def __init__(self):
        super().__init__(
            name="unlurk",
            description="Announce your return from lurking"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "Someone")
        return f"{user} has returned from the shadows! Welcome back! 👋"


class ClipCommand(BaseCommand):
    """Creates a clip of the current stream."""

    def __init__(self, client_id=None, broadcaster_id=None, get_token=None):
        super().__init__(
            name="clip",
            description="Creates a clip of the current stream"
        )
        self.client_id = client_id
        self.broadcaster_id = broadcaster_id
        self.get_token = get_token

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        import asyncio
        import requests as req

        if not self.client_id or not self.broadcaster_id or not self.get_token:
            return "Clip command is not configured."

        token = self.get_token()
        if not token:
            return "No access token available to create clip."

        def create_clip():
            return req.post(
                "https://api.twitch.tv/helix/clips",
                params={"broadcaster_id": self.broadcaster_id},
                headers={
                    "Client-ID": self.client_id,
                    "Authorization": f"Bearer {token}"
                }
            )

        try:
            response = await asyncio.to_thread(create_clip)
            if response.status_code == 202:
                clip_id = response.json()["data"][0]["id"]
                return f"Clip created! https://clips.twitch.tv/{clip_id}"
            elif response.status_code == 401:
                return "Missing clips:edit scope — re-authorize the bot at http://localhost:8080/oauth?scopes=user:read:chat+user:write:chat+user:bot+clips:edit"
            elif response.status_code == 404:
                return "Stream must be live to create a clip."
            else:
                msg = response.json().get("message", "Unknown error")
                return f"Failed to create clip: {msg}"
        except Exception as e:
            return f"Error creating clip: {e}"


class ShoutoutCommand(BaseCommand):
    """Gives a shoutout to another streamer."""

    def __init__(self):
        super().__init__(
            name="so",
            description="Give a shoutout to another streamer"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "someone")
        content = message.text.strip()
        parts = content.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            return f"Usage: !so @username"
        target = parts[1].strip().lstrip("@")
        return f"Go show some love to @{target}! Check them out at https://twitch.tv/{target} PogChamp"


class CommandsCommand(BaseCommand):
    """Lists all available commands in a compact format."""

    def __init__(self, command_handler=None):
        super().__init__(
            name="commands",
            description="Lists all available commands"
        )
        self.command_handler = command_handler

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        if self.command_handler:
            names = sorted(self.command_handler.get_all_commands().keys())
            prefix = self.command_handler.command_prefix
            return "Commands: " + ", ".join(f"{prefix}{name}" for name in names)
        return "Commands: !ping, !hello, !uptime, !about, !help, !commands"


def get_basic_commands() -> list:
    """Get all basic commands.

    Returns:
        List of command instances
    """
    return [
        HelloCommand(),
        UptimeCommand(),
        HelpCommand(),  # Will be configured later
        PingCommand(),
        AboutCommand(),
        LurkCommand(),
        UnlurkCommand(),
        ClipCommand(),  # Will be configured later
        ShoutoutCommand(),
        CommandsCommand()  # Will be configured later
    ]
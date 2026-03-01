"""
Basic commands for the Twitch bot.
"""

import random
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


class SongCommand(BaseCommand):
    """Shows the currently playing song from the Now Playing service."""

    def __init__(self, nowplaying_url=None):
        super().__init__(
            name="song",
            description="Shows the currently playing song"
        )
        self.nowplaying_url = nowplaying_url

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        import asyncio
        import re
        import requests as req

        if not self.nowplaying_url:
            return "NOWPLAYING_URL is not set in .env"

        def fetch_html():
            return req.get(self.nowplaying_url, timeout=5).text

        try:
            html = await asyncio.to_thread(fetch_html)

            title_match = re.search(r'class="sideways-title"[^>]*>([^<]+)</h1>', html)
            artist_match = re.search(r'class="sideways-artist"[^>]*>([^<]+)</h2>', html)
            label_match = re.search(r'class="sideways-label"[^>]*>([^<]+)</h3>', html)

            title = title_match.group(1).strip() if title_match else None
            artist = artist_match.group(1).strip() if artist_match else None
            label = label_match.group(1).strip() if label_match else None

            if title and artist and label:
                return f"Now playing: {title} by {artist} [{label}] 🎵"
            elif title and artist:
                return f"Now playing: {title} by {artist} 🎵"
            elif title:
                return f"Now playing: {title} 🎵"
            else:
                return "Could not read song info from Now Playing service."
        except req.exceptions.ConnectionError:
            return "Cannot connect to Now Playing service. Is VirtualDJ running?"
        except Exception as e:
            return f"Error fetching song info: {e}"


class TimeoutCommand(BaseCommand):
    """Timeout a user (mods only)."""

    def __init__(self, client_id=None, broadcaster_id=None, bot_id=None, get_token=None):
        super().__init__(
            name="timeout",
            description="Timeout a user (mods only) — !timeout @user [seconds]"
        )
        self.client_id = client_id
        self.broadcaster_id = broadcaster_id
        self.bot_id = bot_id
        self.get_token = get_token

    def _is_mod_or_broadcaster(self, message) -> bool:
        try:
            badges = getattr(message.chatter, "badges", []) or []
            for badge in badges:
                badge_id = getattr(badge, "id", getattr(badge, "set_id", ""))
                if badge_id in ("moderator", "broadcaster"):
                    return True
        except Exception:
            pass
        return False

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        import asyncio
        import requests as req

        user = kwargs.get("user", "you")

        if not self._is_mod_or_broadcaster(message):
            return f"@{user} — this command is for mods only."

        broadcaster_id = kwargs.get("broadcaster_id") or self.broadcaster_id
        if not self.client_id or not broadcaster_id or not self.get_token:
            return "Timeout command is not configured."

        content = message.text.strip()
        parts = content.split(None, 2)
        if len(parts) < 2 or not parts[1].strip():
            return "Usage: !timeout @username [seconds]"

        target = parts[1].strip().lstrip("@")
        duration = 60
        if len(parts) >= 3:
            try:
                duration = max(1, min(int(parts[2]), 1209600))
            except ValueError:
                pass

        token = self.get_token()
        if not token:
            return "No access token available."

        def get_user_id():
            r = req.get(
                "https://api.twitch.tv/helix/users",
                params={"login": target},
                headers={"Client-ID": self.client_id, "Authorization": f"Bearer {token}"}
            )
            r.raise_for_status()
            users = r.json().get("data", [])
            return users[0]["id"] if users else None

        def do_timeout(user_id):
            return req.post(
                "https://api.twitch.tv/helix/moderation/bans",
                params={"broadcaster_id": broadcaster_id, "moderator_id": self.bot_id},
                json={"data": {"user_id": user_id, "duration": duration}},
                headers={"Client-ID": self.client_id, "Authorization": f"Bearer {token}"}
            )

        try:
            user_id = await asyncio.to_thread(get_user_id)
            if not user_id:
                return f"User '{target}' not found."

            response = await asyncio.to_thread(do_timeout, user_id)
            if response.status_code == 200:
                return f"@{target} has been timed out for {duration} seconds. ⏱️"
            elif response.status_code == 401:
                return "Missing moderator:manage:banned_users scope — re-authorize the bot."
            elif response.status_code == 403:
                return "The bot needs to be a moderator in the channel."
            else:
                msg = response.json().get("message", "Unknown error")
                return f"Failed to timeout {target}: {msg}"
        except Exception as e:
            return f"Error: {e}"


class EightBallCommand(BaseCommand):
    """Magic 8-ball command."""

    RESPONSES = [
        "It is certain 🎱",
        "Without a doubt 🎱",
        "Yes, definitely 🎱",
        "You may rely on it 🎱",
        "As I see it, yes 🎱",
        "Most likely 🎱",
        "Outlook good 🎱",
        "Signs point to yes 🎱",
        "Reply hazy, try again 🎱",
        "Ask again later 🎱",
        "Better not tell you now 🎱",
        "Cannot predict now 🎱",
        "Concentrate and ask again 🎱",
        "Don't count on it 🎱",
        "My reply is no 🎱",
        "My sources say no 🎱",
        "Outlook not so good 🎱",
        "Very doubtful 🎱",
    ]

    def __init__(self):
        super().__init__(
            name="8ball",
            description="Ask the magic 8-ball a question"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "Someone")
        content = message.text.strip()
        parts = content.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            return f"Usage: !8ball <your question>"
        question = parts[1].strip()
        answer = random.choice(self.RESPONSES)
        return f"@{user} asks: {question} — {answer}"


class HugCommand(BaseCommand):
    """Give a hug to another user."""

    def __init__(self):
        super().__init__(
            name="hug",
            description="Give a hug to someone in chat"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "Someone")
        content = message.text.strip()
        parts = content.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            return f"Usage: !hug @username"
        target = parts[1].strip().lstrip("@")
        return f"{user} gives {target} a big hug! 🤗"


class DiceCommand(BaseCommand):
    """Roll a dice."""

    def __init__(self):
        super().__init__(
            name="dice",
            description="Roll a 6-sided dice"
        )

    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        user = kwargs.get("user", "Someone")
        roll = random.randint(1, 6)
        return f"{user} rolled a {roll}! 🎲"


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

        broadcaster_id = kwargs.get("broadcaster_id") or self.broadcaster_id
        if not self.client_id or not broadcaster_id or not self.get_token:
            return "Clip command is not configured."

        token = self.get_token()
        if not token:
            return "No access token available to create clip."

        def create_clip():
            return req.post(
                "https://api.twitch.tv/helix/clips",
                params={"broadcaster_id": broadcaster_id},
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
        SongCommand(),  # Will be configured later
        TimeoutCommand(),  # Will be configured later
        EightBallCommand(),
        HugCommand(),
        DiceCommand(),
        LurkCommand(),
        UnlurkCommand(),
        ClipCommand(),  # Will be configured later
        ShoutoutCommand(),
        CommandsCommand()  # Will be configured later
    ]
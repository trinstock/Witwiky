"""
Configuration management for the Twitch bot.
"""

import os
from typing import Optional
from dataclasses import dataclass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


@dataclass
class TwitchConfig:
    """Twitch-specific configuration."""
    client_id: str
    client_secret: str
    bot_username: str
    channel_names: list
    redirect_uri: str = "http://localhost:8080"

    @property
    def channel_name(self) -> str:
        """First channel name (backward compat)."""
        return self.channel_names[0] if self.channel_names else ""

    def __post_init__(self):
        """Validate required configuration."""
        if not all([self.client_id, self.client_secret, self.bot_username]):
            raise ValueError("Missing required Twitch configuration")
        if not self.channel_names:
            raise ValueError("At least one channel name is required")


@dataclass
class BotConfig:
    """Bot-specific configuration."""
    command_prefix: str = "!"
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 30
    log_level: str = "INFO"
    nowplaying_url: str = ""
    
    def __post_init__(self):
        """Validate bot configuration."""
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"Invalid log level: {self.log_level}")


@dataclass
class Config:
    """Main configuration class."""
    twitch: TwitchConfig
    bot: BotConfig
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        # Twitch configuration
        # Support comma-separated TWITCH_CHANNEL_NAMES or fallback to TWITCH_CHANNEL_NAME
        raw_channels = os.getenv("TWITCH_CHANNEL_NAMES") or os.getenv("TWITCH_CHANNEL_NAME", "")
        channel_names = [c.strip() for c in raw_channels.split(",") if c.strip()]

        twitch_config = TwitchConfig(
            client_id=os.getenv("TWITCH_CLIENT_ID", ""),
            client_secret=os.getenv("TWITCH_CLIENT_SECRET", ""),
            bot_username=os.getenv("TWITCH_BOT_USERNAME", ""),
            channel_names=channel_names,
            redirect_uri=os.getenv("TWITCH_REDIRECT_URI", "http://localhost:8080")
        )
        
        # Bot configuration
        bot_config = BotConfig(
            command_prefix=os.getenv("COMMAND_PREFIX", "!"),
            max_reconnect_attempts=int(os.getenv("MAX_RECONNECT_ATTEMPTS", "5")),
            reconnect_delay=int(os.getenv("RECONNECT_DELAY", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            nowplaying_url=os.getenv("NOWPLAYING_URL", "")
        )
        
        return cls(twitch=twitch_config, bot=bot_config)
    
    def validate(self) -> None:
        """Validate all configuration settings."""
        self.twitch.__post_init__()
        self.bot.__post_init__()
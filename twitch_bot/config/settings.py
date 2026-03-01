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
    channel_name: str
    redirect_uri: str = "http://localhost:8080"
    
    def __post_init__(self):
        """Validate required configuration."""
        if not all([self.client_id, self.client_secret, self.bot_username]):
            raise ValueError("Missing required Twitch configuration")


@dataclass
class BotConfig:
    """Bot-specific configuration."""
    command_prefix: str = "!"
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 30
    log_level: str = "INFO"
    
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
        twitch_config = TwitchConfig(
            client_id=os.getenv("TWITCH_CLIENT_ID", ""),
            client_secret=os.getenv("TWITCH_CLIENT_SECRET", ""),
            bot_username=os.getenv("TWITCH_BOT_USERNAME", ""),
            channel_name=os.getenv("TWITCH_CHANNEL_NAME", ""),
            redirect_uri=os.getenv("TWITCH_REDIRECT_URI", "http://localhost:8080")
        )
        
        # Bot configuration
        bot_config = BotConfig(
            command_prefix=os.getenv("COMMAND_PREFIX", "!"),
            max_reconnect_attempts=int(os.getenv("MAX_RECONNECT_ATTEMPTS", "5")),
            reconnect_delay=int(os.getenv("RECONNECT_DELAY", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        return cls(twitch=twitch_config, bot=bot_config)
    
    def validate(self) -> None:
        """Validate all configuration settings."""
        self.twitch.__post_init__()
        self.bot.__post_init__()
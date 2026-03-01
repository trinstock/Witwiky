"""Custom exceptions package."""

from .bot_exceptions import (
    BotException,
    AuthenticationError,
    ConnectionError,
    CommandError,
    ConfigurationError,
    RateLimitError
)

__all__ = [
    "BotException",
    "AuthenticationError", 
    "ConnectionError",
    "CommandError",
    "ConfigurationError",
    "RateLimitError"
]
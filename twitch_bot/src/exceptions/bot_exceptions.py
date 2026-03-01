"""Custom exceptions for the Twitch bot."""

from typing import Optional


class BotException(Exception):
    """Base exception class for all bot-related errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize bot exception.
        
        Args:
            message: Main error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details


class AuthenticationError(BotException):
    """Raised when authentication-related errors occur."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class ConnectionError(BotException):
    """Raised when connection-related errors occur."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class CommandError(BotException):
    """Raised when command-related errors occur."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class ConfigurationError(BotException):
    """Raised when configuration-related errors occur."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)


class RateLimitError(BotException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, details)
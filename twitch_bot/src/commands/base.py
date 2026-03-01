"""Base command class for all bot commands."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio

from ..exceptions.bot_exceptions import CommandError


class BaseCommand(ABC):
    """Abstract base class for all bot commands."""
    
    def __init__(self, name: str, description: str = "", aliases: list = None):
        """Initialize base command.
        
        Args:
            name: Command name (without prefix)
            description: Command description for help
            aliases: List of alternative command names
        """
        self.name = name.lower()
        self.description = description
        self.aliases = [alias.lower() for alias in (aliases or [])]
        
    @abstractmethod
    async def execute(self, message: Any, **kwargs) -> Optional[str]:
        """Execute the command.
        
        Args:
            message: The chat message that triggered the command
            **kwargs: Additional context (user, channel, etc.)
            
        Returns:
            Response message to send back, or None
            
        Raises:
            CommandError: If command execution fails
        """
        pass
    
    def matches(self, content: str) -> bool:
        """Check if command matches the given content.
        
        Args:
            content: Message content to check
            
        Returns:
            True if command matches
        """
        # Remove prefix and split into parts
        content = content.strip().lower()
        
        # Check exact name match
        if content == self.name:
            return True
            
        # Check aliases
        if self.aliases and content in self.aliases:
            return True
            
        # Check partial matches (e.g., "hello" matches "hello world")
        if content.startswith(self.name):
            return True
            
        # Check aliases with partial matches
        for alias in self.aliases:
            if content.startswith(alias):
                return True
                
        return False
    
    def get_help(self) -> Dict[str, Any]:
        """Get command help information.
        
        Returns:
            Dictionary with command metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "aliases": self.aliases
        }


class CommandHandler:
    """Manages and executes bot commands."""
    
    def __init__(self, command_prefix: str = "!"):
        """Initialize command handler.
        
        Args:
            command_prefix: Prefix for all commands
        """
        self.command_prefix = command_prefix
        self.commands: Dict[str, BaseCommand] = {}
        
    def register_command(self, command: BaseCommand) -> None:
        """Register a new command.
        
        Args:
            command: Command instance to register
        """
        # Register main name
        self.commands[command.name] = command
        
        # Register aliases
        for alias in command.aliases:
            self.commands[alias] = command
            
    def get_command(self, content: str) -> Optional[BaseCommand]:
        """Get command by name from message content.
        
        Args:
            content: Message content to parse
            
        Returns:
            Command instance if found, None otherwise
        """
        # Remove prefix and get first word as command name
        content = content.strip()
        
        if not content.startswith(self.command_prefix):
            return None
            
        # Remove prefix and get command name
        command_content = content[len(self.command_prefix):].strip()
        
        # Split by whitespace to get just the command name
        parts = command_content.split(None, 1)
        if not parts:
            return None
            
        command_name = parts[0].lower()
        
        # Look up command
        return self.commands.get(command_name)
    
    async def execute_command(self, message: Any, command: BaseCommand, **kwargs) -> Optional[str]:
        """Execute a specific command.
        
        Args:
            message: The chat message
            command: Command to execute
            **kwargs: Additional context
            
        Returns:
            Response message or None
            
        Raises:
            CommandError: If command execution fails
        """
        try:
            return await command.execute(message, **kwargs)
        except Exception as e:
            if isinstance(e, CommandError):
                raise
            else:
                raise CommandError(f"Command '{command.name}' failed: {e}")
    
    def get_all_commands(self) -> Dict[str, BaseCommand]:
        """Get all registered commands.
        
        Returns:
            Dictionary of command name to command instance
        """
        # Return unique commands (not aliases)
        unique_commands = {}
        for name, command in self.commands.items():
            if name == command.name and name not in unique_commands:
                unique_commands[name] = command
        return unique_commands
    
    def get_help_text(self) -> str:
        """Generate help text for all available commands.
        
        Returns:
            Formatted help string
        """
        if not self.commands:
            return "No commands available."
            
        # Get unique commands
        unique_commands = self.get_all_commands()
        
        help_lines = ["Available Commands:"]
        
        for name, command in sorted(unique_commands.items()):
            aliases_text = f" (aliases: {', '.join(command.aliases)})" if command.aliases else ""
            help_lines.append(f"{self.command_prefix}{name} - {command.description}{aliases_text}")
            
        return "\n".join(help_lines)
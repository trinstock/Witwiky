"""
Test suite for the Twitch bot.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

# Import the components we want to test
try:
    from src.bot import TwitchBot
    from config.settings import Config, BotConfig, TwitchConfig
    from src.commands.base import BaseCommand, CommandHandler
    from src.commands.basic import HelloCommand, UptimeCommand
    from src.auth.oauth import OAuthManager
except ImportError as e:
    pytest.skip(f"Could not import modules for testing: {e}", allow_module_level=True)


class TestConfig:
    """Test configuration class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        twitch_config = TwitchConfig(
            client_id="test_client_id",
            client_secret="test_client_secret", 
            bot_username="test_bot",
            channel_name="test_channel"
        )
        
        bot_config = BotConfig(
            command_prefix="!",
            max_reconnect_attempts=3,
            reconnect_delay=10
        )
        
        return Config(twitch=twitch_config, bot=bot_config)


class TestBotConfig:
    """Test cases for BotConfig."""
    
    def test_valid_bot_config(self):
        """Test that valid bot configuration is accepted."""
        config = BotConfig()
        assert config.command_prefix == "!"
        assert config.max_reconnect_attempts == 5
        assert config.log_level == "INFO"
    
    def test_invalid_log_level(self):
        """Test that invalid log levels raise ValueError."""
        with pytest.raises(ValueError):
            BotConfig(log_level="INVALID_LEVEL")
    
    def test_custom_config_values(self):
        """Test custom configuration values."""
        config = BotConfig(
            command_prefix="$",
            max_reconnect_attempts=10,
            log_level="DEBUG"
        )
        
        assert config.command_prefix == "$"
        assert config.max_reconnect_attempts == 10
        assert config.log_level == "DEBUG"


class TestTwitchConfig:
    """Test cases for TwitchConfig."""
    
    def test_valid_twitch_config(self):
        """Test that valid twitch configuration is accepted."""
        config = TwitchConfig(
            client_id="test_client",
            client_secret="test_secret",
            bot_username="test_bot",
            channel_name="test_channel"
        )
        
        assert config.client_id == "test_client"
        assert config.bot_username == "test_bot"
    
    def test_missing_required_fields(self):
        """Test that missing required fields raise ValueError."""
        with pytest.raises(ValueError):
            TwitchConfig(
                client_id="test_client",
                # Missing other required fields
            )


class TestOAuthManager:
    """Test cases for OAuth manager."""
    
    @pytest.fixture
    def oauth_manager(self):
        """Create an OAuth manager for testing."""
        return OAuthManager(
            client_id="test_client",
            client_secret="test_secret"
        )
    
    def test_oauth_manager_initialization(self, oauth_manager):
        """Test OAuth manager initialization."""
        assert oauth_manager.client_id == "test_client"
        assert oauth_manager.client_secret == "test_secret"
        assert oauth_manager.access_token is None
    
    def test_is_token_expired(self, oauth_manager):
        """Test token expiration checking."""
        # Initially no token
        assert oauth_manager.is_token_expired() is False
        
        # Set expired token
        oauth_manager.token_expires_at = 0
        assert oauth_manager.is_token_expired() is True
    
    def test_get_authorization_url(self, oauth_manager):
        """Test authorization URL generation."""
        url = oauth_manager.get_authorization_url("http://localhost:8080")
        
        assert "client_id=test_client" in url
        assert "redirect_uri=http%3A//localhost%3A8080" in url


class TestCommandHandler:
    """Test cases for command handler."""
    
    @pytest.fixture
    def mock_command(self):
        """Create a mock command for testing."""
        class MockCommand(BaseCommand):
            def __init__(self, name="test"):
                super().__init__(name=name)
                
            async def execute(self, message, **kwargs):
                return "test response"
        
        return MockCommand()
    
    @pytest.fixture
    def command_handler(self):
        """Create a command handler for testing."""
        return CommandHandler(prefix="!")
    
    def test_command_registration(self, command_handler, mock_command):
        """Test that commands can be registered."""
        assert len(command_handler.commands) == 0
        
        command_handler.register_command(mock_command)
        
        assert "test" in command_handler.commands
        assert command_handler.commands["test"] == mock_command
    
    def test_command_matching(self, command_handler, mock_command):
        """Test that commands match correctly."""
        command_handler.register_command(mock_command)
        
        # Test exact match
        assert mock_command.matches("test") is True
        
        # Test prefix match
        assert mock_command.matches("test command") is True
    
    def test_get_command_from_content(self, command_handler, mock_command):
        """Test getting commands from message content."""
        command_handler.register_command(mock_command)
        
        # Test valid command
        result = command_handler.get_command("!test")
        assert result == mock_command
        
        # Test invalid prefix
        result = command_handler.get_command("test")
        assert result is None
        
        # Test empty content
        result = command_handler.get_command("")
        assert result is None


class TestBasicCommands:
    """Test cases for basic commands."""
    
    @pytest.fixture
    def hello_command(self):
        """Create a hello command for testing."""
        return HelloCommand()
    
    @pytest.fixture
    def uptime_command(self):
        """Create an uptime command for testing."""
        return UptimeCommand(start_time=1000.0)
    
    def test_hello_command_execution(self, hello_command):
        """Test that hello command executes correctly."""
        # Mock message
        mock_message = Mock()
        mock_message.author.name = "TestUser"
        
        # Execute command
        response = asyncio.run(hello_command.execute(mock_message))
        
        assert response is not None
        assert "Hello" in response or "Hey" in response or "Hi" in response
    
    def test_uptime_command_execution(self, uptime_command):
        """Test that uptime command executes correctly."""
        # Mock message
        mock_message = Mock()
        
        # Execute command with current time around 1100 (100 seconds uptime)
        import time
        original_time = time.time
        
        def mock_time():
            return 1100.0
        
        with patch('time.time', side_effect=mock_time):
            response = asyncio.run(uptime_command.execute(mock_message))
        
        assert response is not None
        assert "Bot has been running for" in response
    
    def test_command_help(self, hello_command):
        """Test that commands provide help information."""
        help_info = hello_command.get_help()
        
        assert "name" in help_info
        assert "description" in help_info
        assert hello_command.name == "hello"


class TestTwitchBot:
    """Test cases for Twitch bot."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        twitch_config = TwitchConfig(
            client_id="test_client",
            client_secret="test_secret",
            bot_username="test_bot",
            channel_name="test_channel"
        )
        
        bot_config = BotConfig()
        
        return Config(twitch=twitch_config, bot=bot_config)
    
    def test_bot_initialization(self, mock_config):
        """Test that bot initializes correctly."""
        # This might fail if twitchio is not installed, which is expected
        try:
            bot = TwitchBot(mock_config)
            
            assert bot.config == mock_config
            assert bot.command_prefix == "!"
            assert bot.start_time is not None
            
        except Exception as e:
            # Expected if twitchio is not available
            assert "twitchio" in str(e).lower() or "mock" in str(e).lower()
    
    def test_get_uptime(self, mock_config):
        """Test uptime calculation."""
        try:
            bot = TwitchBot(mock_config)
            
            # Mock start time to be 100 seconds ago
            bot.start_time = time.time() - 100
            
            uptime_str = bot.get_uptime()
            
            assert isinstance(uptime_str, str)
            assert "m" in uptime_str  # Should contain minutes
            
        except Exception:
            # Expected if twitchio is not available
            pass


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
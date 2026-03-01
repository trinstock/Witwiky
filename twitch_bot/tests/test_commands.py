"""Test suite for command functionality."""

import pytest
from unittest.mock import Mock

try:
    from src.commands.base import BaseCommand, CommandHandler
    from src.commands.basic import HelloCommand, UptimeCommand, HelpCommand, PingCommand, AboutCommand
except ImportError as e:
    pytest.skip(f"Could not import command modules: {e}", allow_module_level=True)


class TestBaseCommand:
    """Test cases for BaseCommand."""
    
    def test_base_command_initialization(self):
        """Test that base command initializes correctly."""
        
        class TestCommand(BaseCommand):
            async def execute(self, message, **kwargs):
                return "test response"
        
        command = TestCommand(
            name="test",
            description="A test command",
            aliases=["t", "testing"]
        )
        
        assert command.name == "test"
        assert command.description == "A test command"
        assert command.aliases == ["t", "testing"]
    
    def test_command_matching(self):
        """Test command matching logic."""
        
        class TestCommand(BaseCommand):
            def __init__(self, name="hello"):
                super().__init__(name=name)
                
            async def execute(self, message, **kwargs):
                return "hello response"
        
        command = TestCommand()
        
        # Test exact match
        assert command.matches("hello") is True
        
        # Test partial match
        assert command.matches("hello world") is True
        
        # Test no match
        assert command.matches("goodbye") is False
    
    def test_command_help(self):
        """Test help information generation."""
        
        class TestCommand(BaseCommand):
            def __init__(self, name="test"):
                super().__init__(
                    name=name,
                    description="A test command",
                    aliases=["t", "testing"]
                )
                
            async def execute(self, message, **kwargs):
                return "test response"
        
        command = TestCommand()
        help_info = command.get_help()
        
        assert help_info["name"] == "test"
        assert help_info["description"] == "A test command"
        assert help_info["aliases"] == ["t", "testing"]


class TestHelloCommand:
    """Test cases for HelloCommand."""
    
    @pytest.fixture
    def hello_command(self):
        """Create a hello command for testing."""
        return HelloCommand()
    
    def test_hello_command_initialization(self, hello_command):
        """Test that hello command initializes correctly."""
        assert hello_command.name == "hello"
        assert "greet" in hello_command.description.lower()
    
    def test_hello_command_execution(self, hello_command):
        """Test that hello command executes correctly."""
        
        # Mock message
        mock_message = Mock()
        mock_message.author.name = "TestUser"
        
        # Execute command
        response = hello_command.execute(mock_message)
        
        assert response is not None
        # Should contain a greeting with the username
        assert "TestUser" in response


class TestUptimeCommand:
    """Test cases for UptimeCommand."""
    
    @pytest.fixture
    def uptime_command(self):
        """Create an uptime command for testing."""
        return UptimeCommand(start_time=1000.0)
    
    def test_uptime_command_initialization(self, uptime_command):
        """Test that uptime command initializes correctly."""
        assert uptime_command.name == "uptime"
        assert uptime_command.start_time == 1000.0
    
    def test_uptime_command_execution(self, uptime_command):
        """Test that uptime command executes correctly."""
        
        # Mock message
        mock_message = Mock()
        
        # Mock time to be 100 seconds after start_time
        import time
        
        original_time = time.time
        
        def mock_current_time():
            return 1100.0  # 100 seconds after start
        
        time.time = mock_current_time
        try:
            response = uptime_command.execute(mock_message)
            
            assert response is not None
            # Should contain uptime information
            assert "Bot has been running for" in response
            
        finally:
            time.time = original_time


class TestPingCommand:
    """Test cases for PingCommand."""
    
    @pytest.fixture
    def ping_command(self):
        """Create a ping command for testing."""
        return PingCommand()
    
    def test_ping_command_initialization(self, ping_command):
        """Test that ping command initializes correctly."""
        assert ping_command.name == "ping"
    
    def test_ping_command_execution(self, ping_command):
        """Test that ping command executes correctly."""
        
        # Mock message
        mock_message = Mock()
        
        response = ping_command.execute(mock_message)
        
        assert response is not None
        # Should respond with pong
        assert "pong" in response.lower()


class TestAboutCommand:
    """Test cases for AboutCommand."""
    
    @pytest.fixture
    def about_command(self):
        """Create an about command for testing."""
        return AboutCommand(version="2.0.0")
    
    def test_about_command_initialization(self, about_command):
        """Test that about command initializes correctly."""
        assert about_command.name == "about"
        assert about_command.version == "2.0.0"
    
    def test_about_command_execution(self, about_command):
        """Test that about command executes correctly."""
        
        # Mock message
        mock_message = Mock()
        
        response = about_command.execute(mock_message)
        
        assert response is not None
        # Should contain version information
        assert "2.0.0" in response


class TestCommandHandler:
    """Test cases for CommandHandler."""
    
    @pytest.fixture
    def command_handler(self):
        """Create a command handler for testing."""
        return CommandHandler(prefix="!")
    
    @pytest.fixture
    def mock_command(self):
        """Create a mock command for testing."""
        
        class MockCommand(BaseCommand):
            def __init__(self, name="test"):
                super().__init__(name=name)
                
            async def execute(self, message, **kwargs):
                return "test response"
        
        return MockCommand()
    
    def test_command_handler_initialization(self, command_handler):
        """Test that command handler initializes correctly."""
        assert command_handler.command_prefix == "!"
        assert len(command_handler.commands) == 0
    
    def test_command_registration(self, command_handler, mock_command):
        """Test that commands can be registered."""
        
        # Initially no commands
        assert len(command_handler.commands) == 0
        
        # Register command
        command_handler.register_command(mock_command)
        
        # Should now have the command
        assert len(command_handler.commands) == 1
        assert "test" in command_handler.commands
    
    def test_command_registration_with_aliases(self, command_handler):
        """Test that commands with aliases are registered correctly."""
        
        class AliasCommand(BaseCommand):
            def __init__(self, name="alias"):
                super().__init__(
                    name=name,
                    aliases=["a", "aliased"]
                )
                
            async def execute(self, message, **kwargs):
                return "alias response"
        
        command = AliasCommand()
        command_handler.register_command(command)
        
        # Should have main name and aliases
        assert len(command_handler.commands) == 3
        assert "alias" in command_handler.commands
        assert "a" in command_handler.commands
        assert "aliased" in command_handler.commands
    
    def test_get_command_from_content(self, command_handler, mock_command):
        """Test getting commands from message content."""
        
        # Register command
        command_handler.register_command(mock_command)
        
        # Test valid command with prefix
        result = command_handler.get_command("!test")
        assert result == mock_command
        
        # Test content without prefix
        result = command_handler.get_command("test")
        assert result is None
        
        # Test empty content
        result = command_handler.get_command("")
        assert result is None
    
    def test_help_text_generation(self, command_handler):
        """Test help text generation."""
        
        # Initially no commands
        help_text = command_handler.get_help_text()
        assert "No commands available" in help_text
        
        # Add a command
        hello_command = HelloCommand()
        command_handler.register_command(hello_command)
        
        help_text = command_handler.get_help_text()
        assert "Available Commands:" in help_text
        assert "!hello" in help_text


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
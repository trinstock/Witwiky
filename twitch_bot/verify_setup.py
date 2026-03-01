"""
Verification script to test the Twitch bot setup and configuration.
"""

import os
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from config.settings import Config, ConfigurationError
    from src.auth.oauth import OAuthManager
    from src.commands.base import CommandHandler
    from src.utils.logger import setup_logger
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)


def test_configuration():
    """Test configuration loading and validation."""
    print("🔧 Testing Configuration...")
    
    try:
        config = Config.from_env()
        config.validate()
        
        print("✅ Configuration loaded successfully")
        print(f"   - Bot Username: {config.twitch.bot_username}")
        print(f"   - Channel Name: {config.twitch.channel_name}")
        print(f"   - Command Prefix: {config.bot.command_prefix}")
        
        return True
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False


def test_oauth_manager():
    """Test OAuth manager initialization."""
    print("\n🔐 Testing OAuth Manager...")
    
    try:
        oauth_manager = OAuthManager(
            client_id="test_client",
            client_secret="test_secret"
        )
        
        print("✅ OAuth manager initialized successfully")
        
        # Test authorization URL generation
        auth_url = oauth_manager.get_authorization_url("http://localhost:8080")
        
        if "client_id=test_client" in auth_url:
            print("✅ Authorization URL generation working")
        else:
            print("❌ Authorization URL generation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ OAuth manager test failed: {e}")
        return False


def test_command_handler():
    """Test command handler functionality."""
    print("\n📝 Testing Command Handler...")
    
    try:
        # Import basic commands
        from src.commands.basic import get_basic_commands
        
        handler = CommandHandler(prefix="!")
        
        # Get and register basic commands
        basic_commands = get_basic_commands()
        for command in basic_commands:
            handler.register_command(command)
        
        print(f"✅ Command handler initialized with {len(handler.commands)} commands")
        
        # Test command lookup
        test_commands = ["!hello", "!uptime", "!ping"]
        
        for cmd in test_commands:
            found_command = handler.get_command(cmd)
            if found_command:
                print(f"✅ Command lookup working: {cmd} -> {found_command.name}")
            else:
                print(f"❌ Command lookup failed: {cmd}")
                return False
        
        # Test help generation
        help_text = handler.get_help_text()
        if "Available Commands:" in help_text:
            print("✅ Help text generation working")
        else:
            print("❌ Help text generation failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Command handler test failed: {e}")
        return False


def test_logging():
    """Test logging configuration."""
    print("\n📋 Testing Logging...")
    
    try:
        logger = setup_logger(
            name="test_bot",
            level="INFO",
            log_file=None  # Don't create actual files during testing
        )
        
        logger.info("Test log message")
        
        print("✅ Logging system working")
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False


def check_environment():
    """Check environment and dependencies."""
    print("\n🔍 Checking Environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}")
    else:
        print(f"❌ Python version too old: {python_version.major}.{python_version.minor} (need 3.8+)")
        return False
    
    # Check required files
    required_files = [
        ".env.example",
        "requirements.txt", 
        "main.py",
        "config/settings.py"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ Missing file: {file_path}")
            return False
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for required variables (without showing values)
        with open(env_file) as f:
            env_content = f.read()
            
        required_vars = [
            "TWITCH_CLIENT_ID",
            "TWITCH_CLIENT_SECRET", 
            "TWITCH_BOT_USERNAME",
            "TWITCH_CHANNEL_NAME"
        ]
        
        for var in required_vars:
            if f"{var}=" in env_content and not f"{var}=your_" in env_content:
                print(f"✅ {var} is set")
            else:
                print(f"❌ {var} is missing or not configured")
                return False
    else:
        print("❌ .env file does not exist (copy from .env.example)")
        return False
    
    return True


def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing Module Imports...")
    
    try:
        # Test core imports
        import twitchio
        
        print("✅ twitchio library available")
        
    except ImportError:
        print("⚠️  twitchio not installed (run: pip install -r requirements.txt)")
        print("   This is expected in some test environments")
    
    try:
        # Test our custom modules
        from src.bot import TwitchBot
        
        print("✅ Custom bot module imports working")
        
    except ImportError as e:
        print(f"❌ Failed to import custom modules: {e}")
        return False
    
    return True


def main():
    """Run all verification tests."""
    print("🚀 Twitch Bot Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Environment Check", check_environment),
        ("Module Imports", test_imports), 
        ("Configuration", test_configuration),
        ("OAuth Manager", test_oauth_manager),
        ("Command Handler", test_command_handler),
        ("Logging System", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot setup looks good.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. Test commands in your Twitch channel")
        print("3. Check SETUP.md for troubleshooting if needed")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the issues above.")
        print("\nCommon solutions:")
        print("1. Copy .env.example to .env and fill in your credentials")
        print("2. Install dependencies: pip install -r requirements.txt") 
        print("3. Check SETUP.md for detailed setup instructions")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
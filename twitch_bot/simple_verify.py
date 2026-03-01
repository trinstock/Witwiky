"""
Simple verification script that doesn't require environment variables.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing Module Imports...")
    
    try:
        # Add src to Python path for imports
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        # Test core imports
        from src.commands.base import BaseCommand, CommandHandler
        print("✅ Core command modules imported")
        
        from src.commands.basic import HelloCommand, UptimeCommand
        print("✅ Basic commands imported")
        
        from src.auth.oauth import OAuthManager
        print("✅ OAuth manager imported") 
        
        from src.exceptions.bot_exceptions import BotException
        print("✅ Custom exceptions imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without environment variables."""
    print("\n🧪 Testing Basic Functionality...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from src.commands.base import BaseCommand, CommandHandler
        from src.commands.basic import HelloCommand, UptimeCommand
        
        # Test command creation
        hello_cmd = HelloCommand()
        uptime_cmd = UptimeCommand(start_time=1000.0)
        
        print(f"✅ Hello command: {hello_cmd.name}")
        print(f"✅ Uptime command: {uptime_cmd.name}")
        
        # Test command handler
        handler = CommandHandler(command_prefix="!")
        handler.register_command(hello_cmd)
        handler.register_command(uptime_cmd)
        
        print(f"✅ Command handler with {len(handler.commands)} commands")
        
        # Test command matching
        test_cmd = handler.get_command("!hello")
        if test_cmd and test_cmd.name == "hello":
            print("✅ Command matching works")
        else:
            print("❌ Command matching failed")
            return False
            
        # Test help generation
        help_text = handler.get_help_text()
        if "Available Commands:" in help_text:
            print("✅ Help generation works")
        else:
            print("❌ Help generation failed") 
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def check_project_structure():
    """Check that all required files exist."""
    print("\n📁 Checking Project Structure...")
    
    required_files = [
        "README.md",
        "requirements.txt", 
        ".env.example",
        "main.py",
        "config/__init__.py",
        "config/settings.py", 
        "src/__init__.py",
        "src/bot.py",
        "src/auth/oauth.py",
        "src/commands/__init__.py",
        "src/commands/base.py", 
        "src/commands/basic.py",
        "src/exceptions/__init__.py",
        "src/exceptions/bot_exceptions.py",
        "src/utils/__init__.py", 
        "src/utils/logger.py",
        "tests/test_bot.py",
        "tests/test_commands.py", 
        "SETUP.md",
        "verify_setup.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} files are missing")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True


def main():
    """Run verification tests."""
    print("🚀 Twitch Bot Project Verification")
    print("=" * 50)
    
    tests = [
        ("Project Structure", check_project_structure),
        ("Module Imports", test_imports), 
        ("Basic Functionality", test_basic_functionality)
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
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All verification tests passed!")
        print("\nYour Twitch bot project is properly structured.")
        print("Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Twitch credentials") 
        print("3. Run: python main.py")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
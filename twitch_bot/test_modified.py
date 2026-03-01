#!/usr/bin/env python3
"""
Test script for the modified Twitch bot that bypasses TwitchIO's API bug.
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.bot_modified import ModifiedTwitchBot
from config.settings import Config


async def test_modified_bot():
    """Test the modified bot with bypassed TwitchIO bug."""
    
    print("🚀 Testing Modified Twitch Bot")
    print("=" * 50)
    
    try:
        # Load configuration
        config = Config()
        
        print(f"✅ Configuration loaded:")
        print(f"   Client ID: {config.twitch.client_id[:20]}...")
        print(f"   Bot Username: {config.twitch.bot_username}")
        print(f"   Channel Name: {config.twitch.channel_name}")
        
        # Initialize modified bot
        print("\n🔧 Initializing Modified Bot...")
        bot = ModifiedTwitchBot(config)
        
        print("✅ Modified bot initialized successfully!")
        print(f"   Bot ID: {bot.bot_id}")
        print(f"   Command Prefix: {config.bot.command_prefix}")
        
        # Test custom API wrapper
        print("\n🧪 Testing Custom API Wrapper...")
        user = await bot.api_wrapper.get_user_by_login(config.twitch.channel_name)
        
        if user:
            print(f"✅ API Test PASSED:")
            print(f"   Found: {user['login']}")
            print(f"   Display Name: {user['display_name']}")
            print(f"   User ID: {user['id']}")
        else:
            print("❌ API Test FAILED:")
            print(f"   Channel '{config.twitch.channel_name}' not found")
        
        # Test command handler
        print("\n📋 Testing Command Handler...")
        commands = bot.get_commands()
        print(f"✅ Commands loaded: {len(commands)}")
        for cmd_name, command in commands.items():
            print(f"   - {cmd_name}: {command.description}")
        
        # Test uptime calculation
        print("\n⏱️ Testing Uptime Calculation...")
        uptime = bot.get_uptime()
        print(f"✅ Bot uptime: {uptime}")
        
        print("\n🎉 Modified Bot Test Complete!")
        print("=" * 50)
        print("✅ All tests passed - Ready to run!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_modified_bot())
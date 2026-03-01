#!/bin/bash

# Quick deployment script for Twitch bot
# This script helps users get started quickly with the bot setup

set -e  # Exit on any error

echo "🚀 Twitch Bot Quick Deployment"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "src" ]; then
    echo "❌ This script must be run from the twitch_bot directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created"
    else
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    
    if [ $? -eq 0 ]; then
        echo "✅ .env file created from template"
        echo ""
        echo "⚠️  IMPORTANT: Edit the .env file with your actual credentials:"
        echo "   - TWITCH_CLIENT_ID"
        echo "   - TWITCH_CLIENT_SECRET" 
        echo "   - TWITCH_BOT_USERNAME"
        echo "   - TWITCH_CHANNEL_NAME"
        echo ""
    else
        echo "❌ Failed to create .env file"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Run verification tests
echo "🔍 Running setup verification..."
python verify_setup.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup verification passed!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your Twitch credentials"
    echo "2. Run: python main.py"
    echo "3. Test commands in your Twitch channel"
else
    echo ""
    echo "⚠️  Setup verification failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🚀 Ready to deploy! Run 'python main.py' to start your bot."
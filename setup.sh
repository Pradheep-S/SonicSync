#!/bin/bash

# SonicSync Setup Script
echo "🎵 Setting up SonicSync - AI Playlist Downloader"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create .env file from example
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cp .env.example .env
    echo "⚠️ Please edit .env file and add your Spotify API credentials"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p downloads temp logs

# Make run.py executable
chmod +x run.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your Spotify API credentials:"
echo "   - Go to https://developer.spotify.com/dashboard"
echo "   - Create a new app"
echo "   - Copy Client ID and Client Secret to .env file"
echo ""
echo "2. Install Chrome/Chromium for web scraping (optional but recommended):"
echo "   Ubuntu/Debian: sudo apt-get install chromium-browser"
echo "   CentOS/RHEL: sudo yum install chromium"
echo "   macOS: brew install --cask google-chrome"
echo ""
echo "3. Start the application:"
echo "   ./run.py  (or python3 run.py)"
echo ""
echo "🌐 The app will be available at http://localhost:5000"

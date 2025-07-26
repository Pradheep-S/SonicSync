#!/usr/bin/env python3
"""
SonicSync Installation Script
Automated setup for the AI Playlist Downloader
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def print_header():
    """Print the installation header"""
    print("🎵" + "="*60 + "🎵")
    print("           SonicSync - AI Playlist Downloader")
    print("                  Installation Script")
    print("🎵" + "="*60 + "🎵")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_git():
    """Check if git is available"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Git not found (optional)")
        return False

def create_virtual_environment():
    """Create a virtual environment"""
    print("\n📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'pip')
    else:
        return os.path.join('venv', 'bin', 'pip')

def get_python_command():
    """Get the correct python command for the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join('venv', 'Scripts', 'python')
    else:
        return os.path.join('venv', 'bin', 'python')

def install_dependencies():
    """Install Python dependencies"""
    print("\n📚 Installing Python packages...")
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    try:
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        print("✅ Pip upgraded")
    except subprocess.CalledProcessError:
        print("⚠️  Could not upgrade pip")
    
    # Install requirements
    try:
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Set up the .env file"""
    print("\n🔧 Setting up environment configuration...")
    
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists('.env.example'):
        try:
            shutil.copy('.env.example', '.env')
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file and add your Spotify API credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        # Create a basic .env file
        env_content = """# Spotify API Credentials (Required)
# Get these from: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# OpenAI API Key (Optional - for enhanced AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=sonic-sync-secret-key-2024
FLASK_ENV=development

# Application Settings
MAX_PLAYLIST_SIZE=500
MAX_FILE_SIZE=104857600
DOWNLOAD_TIMEOUT=30
"""
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ .env file created")
            print("⚠️  Please edit .env file and add your Spotify API credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    directories = ['downloads', 'temp', 'logs']
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created {directory}/ directory")
        except Exception as e:
            print(f"❌ Failed to create {directory}/ directory: {e}")
            return False
    
    return True

def install_chrome_driver():
    """Install Chrome WebDriver for Selenium"""
    print("\n🌐 Setting up Chrome WebDriver...")
    try:
        # The webdriver-manager package will handle this automatically
        print("✅ WebDriver will be installed automatically when needed")
        return True
    except Exception as e:
        print(f"⚠️  WebDriver setup may require manual intervention: {e}")
        return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    python_cmd = get_python_command()
    
    try:
        # Test if we can import the main modules
        test_script = """
import sys
sys.path.insert(0, '.')

try:
    from services.spotify_service import SpotifyService
    print("✅ Spotify service import successful")
except Exception as e:
    print(f"❌ Spotify service import failed: {e}")

try:
    from services.ai_service import AIService
    print("✅ AI service import successful")
except Exception as e:
    print(f"❌ AI service import failed: {e}")

try:
    from services.scraper_service import ScraperService
    print("✅ Scraper service import successful")
except Exception as e:
    print(f"❌ Scraper service import failed: {e}")

try:
    from services.download_service import DownloadService
    print("✅ Download service import successful")
except Exception as e:
    print(f"❌ Download service import failed: {e}")

try:
    import flask
    print(f"✅ Flask {flask.__version__} imported successfully")
except Exception as e:
    print(f"❌ Flask import failed: {e}")
"""
        
        result = subprocess.run([python_cmd, '-c', test_script], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "🎉" + "="*58 + "🎉")
    print("              Installation Complete!")
    print("🎉" + "="*58 + "🎉")
    print()
    print("📋 Next Steps:")
    print()
    print("1. 🔑 Configure Spotify API:")
    print("   • Go to https://developer.spotify.com/dashboard")
    print("   • Create a new app")
    print("   • Copy Client ID and Client Secret to .env file")
    print()
    print("2. 🚀 Start the application:")
    if platform.system() == "Windows":
        print("   • Run: venv\\Scripts\\python run.py")
    else:
        print("   • Run: ./venv/bin/python run.py")
        print("   • Or: source venv/bin/activate && python run.py")
    print()
    print("3. 🌐 Open your browser:")
    print("   • Go to: http://localhost:5000")
    print()
    print("📖 For more information, see README.md")
    print()

def main():
    """Main installation function"""
    print_header()
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    check_git()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup configuration
    if not setup_environment_file():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Setup WebDriver
    install_chrome_driver()
    
    # Test installation
    if test_installation():
        print("✅ Installation test passed")
    else:
        print("⚠️  Installation test had some issues, but may still work")
    
    # Print next steps
    print_next_steps()

if __name__ == '__main__':
    main()

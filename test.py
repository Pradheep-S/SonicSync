#!/usr/bin/env python3
"""
Test script for SonicSync components
Run this to test various functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from services.spotify_service import SpotifyService
        print("✅ Spotify service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Spotify service: {e}")
    
    try:
        from services.scraper_service import ScraperService
        print("✅ Scraper service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Scraper service: {e}")
    
    try:
        from services.ai_service import AIService
        print("✅ AI service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI service: {e}")
    
    try:
        from services.download_service import DownloadService
        print("✅ Download service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Download service: {e}")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask: {e}")

def test_directories():
    """Test if all required directories exist"""
    print("\n📁 Testing directories...")
    
    required_dirs = ['downloads', 'temp', 'logs', 'services', 'templates']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"❌ {directory}/ directory missing")

def test_configuration():
    """Test configuration and environment variables"""
    print("\n⚙️ Testing configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("⚠️ .env file not found (copy from .env.example)")
    
    # Check environment variables
    spotify_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if spotify_id and spotify_secret:
        print("✅ Spotify credentials configured")
    else:
        print("⚠️ Spotify credentials not configured")

def test_ai_functionality():
    """Test AI components"""
    print("\n🧠 Testing AI functionality...")
    
    try:
        from services.ai_service import AIService
        ai_service = AIService()
        
        # Test mood analysis
        test_tracks = [
            {'name': 'Happy Song', 'artist': 'Test Artist'},
            {'name': 'Sad Song', 'artist': 'Test Artist'}
        ]
        
        mood = ai_service.analyze_playlist_mood(test_tracks)
        print(f"✅ Mood analysis working: {mood.get('mood', 'unknown')}")
        
        # Test query enhancement
        enhanced = ai_service.enhance_search_query("Song Name [Original Soundtrack]")
        print(f"✅ Query enhancement working: '{enhanced}'")
        
    except Exception as e:
        print(f"❌ AI functionality test failed: {e}")

def test_basic_services():
    """Test basic service initialization"""
    print("\n🔧 Testing service initialization...")
    
    try:
        from services.spotify_service import SpotifyService
        spotify = SpotifyService()
        print("✅ Spotify service initialized")
    except Exception as e:
        print(f"❌ Spotify service initialization failed: {e}")
    
    try:
        from services.scraper_service import ScraperService
        scraper = ScraperService()
        print("✅ Scraper service initialized")
    except Exception as e:
        print(f"❌ Scraper service initialization failed: {e}")
    
    try:
        from services.download_service import DownloadService
        downloader = DownloadService()
        print("✅ Download service initialized")
    except Exception as e:
        print(f"❌ Download service initialization failed: {e}")

def main():
    """Run all tests"""
    print("🎵 SonicSync Test Suite")
    print("=" * 50)
    
    test_imports()
    test_directories()
    test_configuration()
    test_ai_functionality()
    test_basic_services()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n💡 Tips:")
    print("- If any tests failed, check the requirements.txt installation")
    print("- Configure Spotify API credentials in .env file")
    print("- Install Chrome/Chromium for optimal scraping performance")
    print("- Run 'python run.py' to start the application")

if __name__ == '__main__':
    main()

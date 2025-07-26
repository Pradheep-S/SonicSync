"""
Test suite for SonicSync services
"""
import sys
import os
import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all service modules can be imported without errors"""
    try:
        from services.spotify_service import SpotifyService
        print("✅ SpotifyService imported successfully")
    except Exception as e:
        print(f"❌ SpotifyService import failed: {e}")
        raise

    try:
        from services.scraper_service import ScraperService
        print("✅ ScraperService imported successfully")
    except Exception as e:
        print(f"❌ ScraperService import failed: {e}")
        raise

    try:
        from services.download_service import DownloadService
        print("✅ DownloadService imported successfully")
    except Exception as e:
        print(f"❌ DownloadService import failed: {e}")
        raise

    try:
        from services.ai_service import AIService
        print("✅ AIService imported successfully")
    except Exception as e:
        print(f"❌ AIService import failed: {e}")
        raise

def test_service_initialization():
    """Test that all services can be initialized"""
    from services.spotify_service import SpotifyService
    from services.scraper_service import ScraperService
    from services.download_service import DownloadService
    from services.ai_service import AIService
    
    try:
        spotify = SpotifyService()
        print("✅ SpotifyService initialized successfully")
    except Exception as e:
        print(f"❌ SpotifyService initialization failed: {e}")
        raise

    try:
        scraper = ScraperService()
        print("✅ ScraperService initialized successfully")
    except Exception as e:
        print(f"❌ ScraperService initialization failed: {e}")
        raise

    try:
        downloader = DownloadService()
        print("✅ DownloadService initialized successfully")
    except Exception as e:
        print(f"❌ DownloadService initialization failed: {e}")
        raise

    try:
        ai = AIService()
        print("✅ AIService initialized successfully")
    except Exception as e:
        print(f"❌ AIService initialization failed: {e}")
        raise

def test_flask_app():
    """Test that Flask app can be imported and created"""
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        
        # Test that routes are registered
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Main route working")
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        raise

if __name__ == "__main__":
    print("🧪 Running SonicSync Service Tests...")
    print("=" * 50)
    
    print("\n1. Testing imports...")
    test_imports()
    
    print("\n2. Testing service initialization...")
    test_service_initialization()
    
    print("\n3. Testing Flask app...")
    test_flask_app()
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! SonicSync is ready to run.")

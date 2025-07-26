import os
import logging
from datetime import datetime

def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"sonicsync_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

def validate_spotify_url(url):
    """Validate if URL is a valid Spotify playlist URL"""
    spotify_patterns = [
        'open.spotify.com/playlist/',
        'spotify.com/playlist/',
        'spotify:playlist:'
    ]
    
    return any(pattern in url for pattern in spotify_patterns)

def clean_string_for_search(text):
    """Clean and optimize string for search"""
    import re
    
    # Remove special characters and extra spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = ' '.join(text.split())
    
    return text.strip()

def format_duration(duration_ms):
    """Format duration from milliseconds to MM:SS format"""
    if not duration_ms:
        return "0:00"
    
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    
    return f"{minutes}:{seconds:02d}"

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def ensure_directories():
    """Ensure all necessary directories exist"""
    directories = ['downloads', 'temp', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_config():
    """Get application configuration"""
    return {
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'max_playlist_size': 500,  # Max tracks per playlist
        'download_timeout': 30,  # Seconds
        'supported_formats': ['.mp3', '.m4a', '.wav', '.flac', '.aac'],
        'rate_limit_delay': 1,  # Seconds between downloads
        'max_retries': 3,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

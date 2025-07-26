#!/usr/bin/env python3
"""
SonicSync - AI Playlist Downloader
Run this script to start the Flask application
"""

from app import app
from utils import setup_logging, ensure_directories
import os

if __name__ == '__main__':
    # Setup logging
    setup_logging()
    
    # Ensure directories exist
    ensure_directories()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )

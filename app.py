from flask import Flask, request, render_template, send_file, jsonify, flash, redirect, url_for
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import zipfile
import shutil
import time
import threading
from utils import setup_logging, ensure_directories, validate_spotify_url, get_config

# Load environment variables
load_dotenv()

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'sonic-sync-secret-key-2024')

# Ensure directories exist
ensure_directories()

# Initialize services with error handling
try:
    from services.spotify_service import SpotifyService
    from services.scraper_service import ScraperService
    from services.ai_service import AIService
    from services.download_service import DownloadService
    
    spotify_service = SpotifyService()
    scraper_service = ScraperService()
    ai_service = AIService()
    download_service = DownloadService()
    
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    raise

@app.route('/')
def index():
    """Main page with the playlist input form"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    """Analyze Spotify playlist and return track information"""
    try:
        data = request.get_json()
        playlist_url = data.get('playlist_url')
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        # Validate Spotify URL
        if not validate_spotify_url(playlist_url):
            return jsonify({'error': 'Invalid Spotify playlist URL'}), 400
        
        logger.info(f"Analyzing playlist: {playlist_url}")
        
        # Get playlist info first
        try:
            playlist_info = spotify_service.get_playlist_info(playlist_url)
            logger.info(f"Playlist: {playlist_info['name']} by {playlist_info['owner']}")
        except Exception as e:
            logger.warning(f"Could not get playlist info: {str(e)}")
            playlist_info = {}
        
        # Get tracks from Spotify
        tracks = spotify_service.get_playlist_tracks(playlist_url)
        
        if not tracks:
            return jsonify({'error': 'No tracks found or invalid playlist URL'}), 400
        
        # Limit tracks if too many
        config = get_config()
        if len(tracks) > config['max_playlist_size']:
            tracks = tracks[:config['max_playlist_size']]
            logger.warning(f"Playlist truncated to {config['max_playlist_size']} tracks")
        
        # Analyze playlist mood (optional AI feature)
        mood_analysis = {}
        try:
            mood_analysis = ai_service.analyze_playlist_mood(tracks)
        except Exception as e:
            logger.warning(f"Mood analysis failed: {str(e)}")
            mood_analysis = {"mood": "unknown", "confidence": 0.0}
        
        return jsonify({
            'tracks': tracks,
            'total_tracks': len(tracks),
            'playlist_info': playlist_info,
            'mood_analysis': mood_analysis,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error analyzing playlist: {str(e)}")
        return jsonify({'error': f'Error analyzing playlist: {str(e)}'}), 500

@app.route('/api/download', methods=['POST'])
def download_playlist():
    """Download the entire playlist as a ZIP file"""
    try:
        data = request.get_json()
        playlist_url = data.get('playlist_url')
        
        if not playlist_url:
            return jsonify({'error': 'Playlist URL is required'}), 400
        
        # Validate Spotify URL
        if not validate_spotify_url(playlist_url):
            return jsonify({'error': 'Invalid Spotify playlist URL'}), 400
        
        logger.info(f"Starting download for playlist: {playlist_url}")
        
        # Get tracks from Spotify
        tracks = spotify_service.get_playlist_tracks(playlist_url)
        
        if not tracks:
            return jsonify({'error': 'No tracks found or invalid playlist URL'}), 400
        
        # Limit tracks if too many
        config = get_config()
        if len(tracks) > config['max_playlist_size']:
            tracks = tracks[:config['max_playlist_size']]
        
        # Create unique folder for this download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        download_folder = f"downloads/playlist_{timestamp}"
        os.makedirs(download_folder, exist_ok=True)
        
        successful_downloads = []
        failed_downloads = []
        
        # Process each track
        for i, track in enumerate(tracks):
            try:
                logger.info(f"Processing track {i+1}/{len(tracks)}: {track['name']} by {track['artist']}")
                
                # Create search query
                search_query = f"{track['name']} {track['artist']}"
                enhanced_query = ai_service.enhance_search_query(search_query)
                
                # Search for the song
                search_results = scraper_service.search_masstamilan(enhanced_query)
                
                if search_results:
                    # Use AI to find the best match
                    best_match = ai_service.get_best_match(search_query, search_results)
                    
                    if best_match:
                        # Try to download the song
                        preferred_name = f"{i+1:02d}_{track['name']} - {track['artist']}"
                        success = download_service.download_song(best_match, download_folder, preferred_name)
                        
                        if success:
                            successful_downloads.append(track)
                            logger.info(f"✅ Downloaded: {track['name']}")
                        else:
                            failed_downloads.append(track)
                            logger.warning(f"❌ Failed to download: {track['name']}")
                    else:
                        failed_downloads.append(track)
                        logger.warning(f"❌ No suitable match found: {track['name']}")
                else:
                    failed_downloads.append(track)
                    logger.warning(f"❌ No search results for: {track['name']}")
                
                # Add delay between downloads to be respectful
                time.sleep(config.get('rate_limit_delay', 1))
                    
            except Exception as e:
                logger.error(f"Error processing track {track['name']}: {str(e)}")
                failed_downloads.append(track)
        
        # Create ZIP file if we have any downloads
        zip_filename = f"playlist_{timestamp}.zip"
        zip_path = f"downloads/{zip_filename}"
        
        if successful_downloads:
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(download_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, download_folder)
                            zipf.write(file_path, arcname)
                
                logger.info(f"Created ZIP file: {zip_filename}")
            except Exception as e:
                logger.error(f"Error creating ZIP file: {str(e)}")
                return jsonify({'error': 'Failed to create ZIP file'}), 500
        else:
            # No successful downloads
            return jsonify({
                'error': 'No songs could be downloaded',
                'successful_downloads': 0,
                'failed_downloads': len(failed_downloads),
                'total_tracks': len(tracks)
            }), 400
        
        # Clean up temporary folder
        try:
            shutil.rmtree(download_folder)
        except Exception as e:
            logger.warning(f"Could not clean up temp folder: {str(e)}")
        
        return jsonify({
            'download_url': f'/download/{zip_filename}',
            'successful_downloads': len(successful_downloads),
            'failed_downloads': len(failed_downloads),
            'total_tracks': len(tracks),
            'zip_filename': zip_filename,
            'success_rate': len(successful_downloads) / len(tracks) if tracks else 0
        })
    
    except Exception as e:
        logger.error(f"Error downloading playlist: {str(e)}")
        return jsonify({'error': f'Error downloading playlist: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Serve the downloaded ZIP file"""
    try:
        file_path = os.path.join('downloads', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error serving file: {str(e)}")
        return jsonify({'error': 'Error serving file'}), 500

@app.route('/api/search', methods=['POST'])
def search_single_track():
    """Search for a single track"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        logger.info(f"Searching for: {query}")
        
        # Enhance the query with AI
        enhanced_query = ai_service.enhance_search_query(query)
        
        # Search for the song
        search_results = scraper_service.search_masstamilan(enhanced_query)
        
        # If no results with enhanced query, try original
        if not search_results and enhanced_query != query:
            search_results = scraper_service.search_masstamilan(query)
        
        return jsonify({
            'query': query,
            'enhanced_query': enhanced_query,
            'results': search_results[:10],  # Limit to top 10 results
            'total_results': len(search_results)
        })
    
    except Exception as e:
        logger.error(f"Error searching track: {str(e)}")
        return jsonify({'error': f'Error searching track: {str(e)}'}), 500

@app.route('/api/status')
def get_status():
    """Get application status and service health"""
    try:
        status = {
            'app_status': 'running',
            'services': {
                'spotify': 'available' if spotify_service.sp else 'unavailable',
                'ai': 'available' if ai_service.model else 'unavailable',
                'scraper': 'available',
                'downloader': 'available'
            },
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': 'Error getting status'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    # Ensure directories exist
    ensure_directories()
    
    # Log startup information
    logger.info("🎵 Starting SonicSync - AI Playlist Downloader")
    logger.info(f"Flask Environment: {os.getenv('FLASK_ENV', 'production')}")
    logger.info(f"Debug Mode: {os.getenv('FLASK_ENV') == 'development'}")
    
    # Check service status
    logger.info("🔧 Service Status:")
    logger.info(f"  Spotify: {'✅' if spotify_service.sp else '❌'}")
    logger.info(f"  AI Service: {'✅' if ai_service.model else '❌'}")
    logger.info(f"  Scraper: ✅")
    logger.info(f"  Downloader: ✅")
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🌐 Starting server on http://localhost:{port}")
    app.run(debug=debug, host='0.0.0.0', port=port)

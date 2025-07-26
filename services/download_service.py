import requests
import os
import logging
import time
from urllib.parse import urlparse
import mimetypes
import re

logger = logging.getLogger(__name__)

class DownloadService:
    """Service for downloading music files"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Supported audio formats
        self.supported_formats = ['.mp3', '.m4a', '.wav', '.flac', '.aac']
        
        # Maximum file size (100MB)
        self.max_file_size = 100 * 1024 * 1024
    
    def sanitize_filename(self, filename):
        """Sanitize filename for safe storage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = ' '.join(filename.split())
        filename = filename[:100]  # Limit to 100 characters
        
        return filename
    
    def download_song(self, song_info, download_folder, preferred_name=None):
        """Download a song from the provided information with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if isinstance(song_info, dict):
                    song_url = song_info.get('url')
                    song_title = song_info.get('title', 'Unknown Song')
                else:
                    song_url = str(song_info)
                    song_title = 'Unknown Song'
                
                if not song_url:
                    logger.error("No URL provided for download")
                    return False
                
                logger.info(f"📥 Downloading attempt {attempt + 1}/{max_retries}: {song_title}")
                
                # Get download links from the song page
                from services.scraper_service import ScraperService
                scraper = ScraperService()
                download_links = scraper.get_download_links(song_url)
                
                if not download_links:
                    # Try with Selenium as fallback
                    logger.info("Trying Selenium fallback...")
                    download_links = scraper.get_download_links_selenium(song_url)
                
                if not download_links:
                    logger.warning(f"No download links found for: {song_title}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                        continue
                    return False
                
                # Try each download link until one works
                for i, link in enumerate(download_links):
                    try:
                        logger.debug(f"Trying download link {i + 1}/{len(download_links)}")
                        
                        # Validate the link first
                        if not self.validate_download_link(link):
                            logger.debug(f"Link validation failed: {link}")
                            continue
                        
                        if self._download_file(link, download_folder, preferred_name or song_title):
                            logger.info(f"✅ Successfully downloaded: {song_title}")
                            return True
                            
                    except Exception as e:
                        logger.warning(f"Failed to download from {link}: {str(e)}")
                        continue
                
                logger.warning(f"All download links failed for: {song_title} (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(3)  # Wait longer between attempts
                    
            except Exception as e:
                logger.error(f"Error in download attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        logger.error(f"❌ All download attempts failed for: {song_title}")
        return False
    
    def validate_download_link(self, url):
        """Validate if a download link is working and points to audio"""
        try:
            # Quick check - does URL look like audio?
            if any(ext in url.lower() for ext in self.supported_formats):
                return True
            
            # Check with HEAD request
            response = self.session.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                return False
            
            content_type = response.headers.get('content-type', '').lower()
            content_length = response.headers.get('content-length')
            
            # Check if it's audio content
            is_audio = ('audio' in content_type or 'mpeg' in content_type or 
                       'mp3' in content_type or 'mp4' in content_type)
            
            # Check file size (should be reasonable for a song)
            if content_length:
                size = int(content_length)
                # Songs should be between 1MB and 100MB typically
                if size < 1024 * 1024 or size > self.max_file_size:
                    return False
            
            return is_audio
            
        except Exception as e:
            logger.debug(f"Link validation failed: {str(e)}")
            return False
    
    def _download_file(self, url, download_folder, filename):
        """Download a file from URL"""
        try:
            # Validate URL
            if not url or not url.startswith('http'):
                return False
            
            # Check if it's likely an audio file
            if not any(fmt in url.lower() for fmt in self.supported_formats):
                # Try to get content type
                try:
                    head_response = self.session.head(url, timeout=10)
                    content_type = head_response.headers.get('content-type', '').lower()
                    if not ('audio' in content_type or 'mpeg' in content_type):
                        logger.warning(f"URL doesn't appear to be an audio file: {url}")
                        return False
                except:
                    pass
            
            # Start download
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length:
                content_length = int(content_length)
                if content_length > self.max_file_size:
                    logger.warning(f"File too large: {content_length} bytes")
                    return False
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                ext = '.mp3'
            elif 'audio/mp4' in content_type or 'audio/m4a' in content_type:
                ext = '.m4a'
            else:
                # Try to get extension from URL
                parsed_url = urlparse(url)
                url_ext = os.path.splitext(parsed_url.path)[1].lower()
                ext = url_ext if url_ext in self.supported_formats else '.mp3'
            
            # Sanitize filename and add extension
            safe_filename = self.sanitize_filename(filename)
            if not safe_filename.lower().endswith(tuple(self.supported_formats)):
                safe_filename += ext
            
            # Full file path
            file_path = os.path.join(download_folder, safe_filename)
            
            # Download the file
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Check size limit during download
                        if downloaded_size > self.max_file_size:
                            f.close()
                            os.remove(file_path)
                            logger.warning("File too large, download cancelled")
                            return False
            
            # Verify the downloaded file
            if os.path.exists(file_path) and os.path.getsize(file_path) > 1024:  # At least 1KB
                logger.info(f"Downloaded: {safe_filename} ({downloaded_size} bytes)")
                return True
            else:
                # Clean up failed download
                if os.path.exists(file_path):
                    os.remove(file_path)
                return False
                
        except Exception as e:
            logger.error(f"Error downloading file from {url}: {str(e)}")
            return False
    
    def download_multiple_songs(self, song_list, download_folder, progress_callback=None):
        """Download multiple songs with progress tracking"""
        try:
            os.makedirs(download_folder, exist_ok=True)
            
            successful_downloads = []
            failed_downloads = []
            
            total_songs = len(song_list)
            
            for i, song_info in enumerate(song_list):
                try:
                    if progress_callback:
                        progress_callback(i, total_songs, song_info)
                    
                    # Add a small delay between downloads to be respectful
                    if i > 0:
                        time.sleep(1)
                    
                    success = self.download_song(song_info, download_folder, f"{i+1:02d}_{song_info.get('name', 'song')}")
                    
                    if success:
                        successful_downloads.append(song_info)
                    else:
                        failed_downloads.append(song_info)
                        
                except Exception as e:
                    logger.error(f"Error processing song {i+1}: {str(e)}")
                    failed_downloads.append(song_info)
            
            return {
                'successful': successful_downloads,
                'failed': failed_downloads,
                'total': total_songs,
                'success_rate': len(successful_downloads) / total_songs if total_songs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error downloading multiple songs: {str(e)}")
            return {
                'successful': [],
                'failed': song_list,
                'total': len(song_list),
                'success_rate': 0,
                'error': str(e)
            }
    
    def get_file_info(self, file_path):
        """Get information about a downloaded file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            return {
                'filename': os.path.basename(file_path),
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'extension': os.path.splitext(file_path)[1],
                'mime_type': mimetypes.guess_type(file_path)[0]
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return None

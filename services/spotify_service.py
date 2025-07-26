import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import logging
import re

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service for interacting with Spotify Web API"""
    
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            logger.warning("Spotify credentials not found. Some features may not work.")
            self.sp = None
        else:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                logger.info("Spotify service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Spotify service: {str(e)}")
                self.sp = None
    
    def extract_playlist_id(self, playlist_url):
        """Extract playlist ID from Spotify URL"""
        try:
            # Handle different Spotify URL formats
            patterns = [
                r'playlist/([a-zA-Z0-9]+)',
                r'playlist:([a-zA-Z0-9]+)',
                r'/playlist/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, playlist_url)
                if match:
                    return match.group(1)
            
            # If it's just the ID
            if re.match(r'^[a-zA-Z0-9]+$', playlist_url):
                return playlist_url
                
            return None
        except Exception as e:
            logger.error(f"Error extracting playlist ID: {str(e)}")
            return None
    
    def get_playlist_tracks(self, playlist_url):
        """Get all tracks from a Spotify playlist"""
        try:
            if not self.sp:
                raise Exception("Spotify service not available. Please check your credentials.")
            
            playlist_id = self.extract_playlist_id(playlist_url)
            if not playlist_id:
                raise Exception("Invalid Spotify playlist URL")
            
            logger.info(f"Fetching tracks for playlist: {playlist_id}")
            
            tracks = []
            results = self.sp.playlist_tracks(playlist_id, limit=100)
            
            while results:
                for item in results['items']:
                    if item['track'] and item['track']['name']:
                        track = item['track']
                        
                        # Extract track information
                        track_info = {
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'] if track['album'] else '',
                            'duration_ms': track['duration_ms'],
                            'popularity': track['popularity'],
                            'preview_url': track['preview_url'],
                            'spotify_url': track['external_urls']['spotify'],
                            'id': track['id']
                        }
                        
                        tracks.append(track_info)
                
                # Check if there are more tracks
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            logger.info(f"Successfully fetched {len(tracks)} tracks")
            return tracks
            
        except Exception as e:
            logger.error(f"Error fetching playlist tracks: {str(e)}")
            raise
    
    def get_playlist_info(self, playlist_url):
        """Get playlist metadata"""
        try:
            if not self.sp:
                raise Exception("Spotify service not available")
            
            playlist_id = self.extract_playlist_id(playlist_url)
            if not playlist_id:
                raise Exception("Invalid Spotify playlist URL")
            
            playlist = self.sp.playlist(playlist_id)
            
            return {
                'name': playlist['name'],
                'description': playlist['description'],
                'owner': playlist['owner']['display_name'],
                'total_tracks': playlist['tracks']['total'],
                'public': playlist['public'],
                'followers': playlist['followers']['total'],
                'image_url': playlist['images'][0]['url'] if playlist['images'] else None
            }
            
        except Exception as e:
            logger.error(f"Error fetching playlist info: {str(e)}")
            raise
    
    def search_track(self, query, limit=10):
        """Search for tracks on Spotify"""
        try:
            if not self.sp:
                raise Exception("Spotify service not available")
            
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track in results['tracks']['items']:
                track_info = {
                    'name': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'preview_url': track['preview_url'],
                    'spotify_url': track['external_urls']['spotify'],
                    'id': track['id']
                }
                tracks.append(track_info)
            
            return tracks
            
        except Exception as e:
            logger.error(f"Error searching tracks: {str(e)}")
            raise

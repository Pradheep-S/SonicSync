# 🎵 SonicSync - Technical Documentation

## 🏗️ Architecture Overview

SonicSync is built using a modular Python architecture with the following components:

### Core Services

1. **Spotify Service** (`services/spotify_service.py`)
   - Handles Spotify Web API integration
   - Extracts playlist information and tracks
   - Manages authentication using Client Credentials flow

2. **AI Service** (`services/ai_service.py`)
   - Powers intelligent song matching using sentence-transformers
   - Provides mood analysis for playlists
   - Enhances search queries for better results
   - Optional OpenAI integration for advanced features

3. **Scraper Service** (`services/scraper_service.py`)
   - Web scraping from music sources (masstamilan.dev)
   - Multiple fallback strategies (requests + Selenium)
   - Intelligent result filtering and deduplication

4. **Download Service** (`services/download_service.py`)
   - Manages file downloads with retry logic
   - Validates audio files and download links
   - Handles batch downloads with progress tracking

### Flask Application (`app.py`)

The main web application provides:
- REST API endpoints for playlist analysis and downloads
- Web interface for user interaction
- Error handling and logging
- ZIP file generation and serving

## 🔧 How It Works

### Step 1: Playlist Analysis

```python
# User submits Spotify playlist URL
playlist_url = "https://open.spotify.com/playlist/..."

# Extract playlist ID and validate
playlist_id = spotify_service.extract_playlist_id(playlist_url)

# Fetch all tracks using Spotify API
tracks = spotify_service.get_playlist_tracks(playlist_url)

# AI analyzes playlist mood
mood = ai_service.analyze_playlist_mood(tracks)
```

### Step 2: AI-Powered Search

```python
for track in tracks:
    # Create search query
    query = f"{track['name']} {track['artist']}"
    
    # Enhance query with AI
    enhanced_query = ai_service.enhance_search_query(query)
    
    # Search music sources
    results = scraper_service.search_masstamilan(enhanced_query)
    
    # Find best match using semantic similarity
    best_match = ai_service.get_best_match(query, results)
```

### Step 3: Intelligent Download

```python
# Download with retry logic
success = download_service.download_song(best_match, folder, filename)

# Validate downloaded files
if success and validate_audio_file(downloaded_file):
    successful_downloads.append(track)
else:
    failed_downloads.append(track)
```

### Step 4: ZIP Package Creation

```python
# Create ZIP file with all downloaded songs
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in downloaded_files:
        zipf.write(file_path, arcname=filename)
```

## 🧠 AI Components Deep Dive

### Semantic Matching

Uses `sentence-transformers` library with the `all-MiniLM-L6-v2` model:

```python
def get_best_match(self, query, candidates):
    # Encode query and candidates
    query_embedding = self.model.encode(query, convert_to_tensor=True)
    candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
    
    # Calculate cosine similarities
    similarities = util.cos_sim(query_embedding, candidate_embeddings)[0]
    
    # Return best match
    best_idx = similarities.argmax().item()
    return candidates[best_idx]
```

### Mood Analysis

Analyzes track names and artists to determine playlist mood:

```python
def analyze_playlist_mood(self, tracks):
    # Define mood keywords
    mood_keywords = {
        "energetic": ["dance", "party", "energy", "pump", "power"],
        "romantic": ["love", "heart", "kiss", "romantic", "valentine"],
        "sad": ["sad", "cry", "tears", "alone", "miss"],
        # ... more moods
    }
    
    # Score each mood based on keyword frequency
    for mood, keywords in mood_keywords.items():
        score = sum(1 for keyword in keywords if keyword in playlist_text)
        mood_scores[mood] = score
    
    # Return dominant mood with confidence
    return {"mood": dominant_mood, "confidence": confidence}
```

### Query Enhancement

Cleans and optimizes search queries:

```python
def enhance_search_query(self, original_query):
    # Remove noise words
    keywords_to_remove = [
        'original soundtrack', 'ost', 'feat', 'featuring', 
        'remix', 'version', 'remastered'
    ]
    
    # Clean special characters
    query = re.sub(r'[^\w\s]', ' ', query)
    
    # Extract main components
    if ' by ' in query:
        song_name, artist = query.split(' by ', 1)
        return f"{song_name.strip()} {artist.strip()}"
    
    return query.strip()
```

## 🔍 Web Scraping Strategy

### Multi-Strategy Approach

1. **Direct HTTP Requests**
   ```python
   response = self.session.get(search_url, timeout=15)
   soup = BeautifulSoup(response.text, 'html.parser')
   ```

2. **Selenium WebDriver (Fallback)**
   ```python
   driver = webdriver.Chrome(options=chrome_options)
   driver.get(search_url)
   time.sleep(3)  # Wait for JavaScript
   ```

3. **Multiple Query Variations**
   ```python
   variations = [
       original_query,
       query_without_artist,
       query_with_replacements,
       simplified_query
   ]
   ```

### Result Filtering

```python
def _filter_and_deduplicate_results(self, results):
    seen_urls = set()
    filtered_results = []
    
    for result in results:
        url = result.get('url', '')
        title = result.get('title', '').lower().strip()
        
        # Skip duplicates and low-quality results
        if url not in seen_urls and len(title) > 5:
            if not any(word in title for word in ['ad', 'promo']):
                filtered_results.append(result)
                seen_urls.add(url)
    
    return filtered_results
```

## 📁 File Management

### Download Validation

```python
def validate_download_link(self, url):
    # Check content type
    response = self.session.head(url, timeout=10)
    content_type = response.headers.get('content-type', '').lower()
    
    # Validate as audio
    is_audio = ('audio' in content_type or 'mpeg' in content_type)
    
    # Check file size (1MB - 100MB)
    content_length = response.headers.get('content-length')
    if content_length:
        size = int(content_length)
        if size < 1024*1024 or size > 100*1024*1024:
            return False
    
    return is_audio
```

### Safe Filename Generation

```python
def sanitize_filename(self, filename):
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length and clean spaces
    filename = ' '.join(filename.split())
    return filename[:100]
```

## 🌐 API Endpoints

### `/api/analyze` (POST)
Analyzes a Spotify playlist and returns track information.

**Request:**
```json
{
  "playlist_url": "https://open.spotify.com/playlist/..."
}
```

**Response:**
```json
{
  "tracks": [...],
  "total_tracks": 25,
  "playlist_info": {...},
  "mood_analysis": {
    "mood": "energetic",
    "confidence": 0.8,
    "description": "..."
  },
  "status": "success"
}
```

### `/api/download` (POST)
Downloads the entire playlist as a ZIP file.

**Request:**
```json
{
  "playlist_url": "https://open.spotify.com/playlist/..."
}
```

**Response:**
```json
{
  "download_url": "/download/playlist_20231225_120000.zip",
  "successful_downloads": 20,
  "failed_downloads": 5,
  "total_tracks": 25,
  "success_rate": 0.8,
  "zip_filename": "playlist_20231225_120000.zip"
}
```

### `/api/search` (POST)
Searches for a single track.

**Request:**
```json
{
  "query": "Shape of You Ed Sheeran"
}
```

**Response:**
```json
{
  "query": "Shape of You Ed Sheeran",
  "enhanced_query": "shape you ed sheeran",
  "results": [...],
  "total_results": 15
}
```

### `/api/status` (GET)
Returns application status and service health.

**Response:**
```json
{
  "app_status": "running",
  "services": {
    "spotify": "available",
    "ai": "available",
    "scraper": "available",
    "downloader": "available"
  },
  "version": "1.0.0",
  "timestamp": "2023-12-25T12:00:00"
}
```

## 🔒 Security Considerations

### Input Validation
- URL validation for Spotify playlists
- Sanitization of filenames and search queries
- Rate limiting to prevent abuse

### File Safety
- File type validation (audio only)
- Size limits (max 100MB per file)
- Secure temporary file handling

### Network Security
- User-Agent headers to identify as legitimate client
- Request timeouts to prevent hanging
- Retry logic with exponential backoff

## 🚀 Performance Optimizations

### Caching
- Session reuse for HTTP requests
- Model loading optimization for AI components

### Concurrent Processing
- Async/await patterns for I/O operations
- Batch processing for multiple downloads

### Memory Management
- Streaming downloads for large files
- Cleanup of temporary files
- Garbage collection for large datasets

## 🐛 Error Handling

### Graceful Degradation
```python
try:
    # Try advanced AI matching
    result = ai_service.get_best_match(query, candidates)
except Exception:
    # Fallback to simple string matching
    result = fallback_string_match(query, candidates)
```

### Retry Logic
```python
for attempt in range(max_retries):
    try:
        return download_file(url)
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
        raise e
```

### Comprehensive Logging
```python
import logging

logger = logging.getLogger(__name__)

# Different log levels for different scenarios
logger.info("Starting download process")
logger.warning("No search results found, trying fallback")
logger.error("Download failed after all retries")
logger.debug("Processing track 1/25")
```

## 📊 Monitoring and Analytics

### Success Metrics
- Download success rate per playlist
- Average processing time per track
- AI matching accuracy scores
- User engagement metrics

### Error Tracking
- Failed download reasons
- Common search failures
- Performance bottlenecks
- Resource usage patterns

## 🔮 Future Enhancements

### Planned Features
1. **Enhanced AI Integration**
   - GPT-4 for better query understanding
   - Music genre classification
   - Personalized recommendations

2. **Multiple Source Support**
   - YouTube Music integration
   - SoundCloud support
   - Local music library scanning

3. **Advanced Features**
   - Playlist collaboration
   - Social sharing
   - Music discovery based on mood
   - Real-time download progress

4. **Performance Improvements**
   - Redis caching
   - CDN integration
   - Distributed processing
   - Progressive web app features

### Technical Debt
- Refactor scraping logic for better maintainability
- Add comprehensive unit tests
- Implement proper database for persistence
- Add metrics and monitoring dashboard

---

This technical documentation provides a deep dive into how SonicSync works. For user-facing documentation, see the main README.md file.

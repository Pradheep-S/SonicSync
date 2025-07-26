# 🎵 SonicSync - AI Playlist Downloader

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![AI](https://img.shields.io/badge/AI-Powered-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

SonicSync is an intelligent AI-powered playlist downloader that transforms your Spotify playlists into downloadable music collections. Using advanced AI matching algorithms, it finds and downloads the best quality songs from various sources.

## ✨ Features

- 🎧 **Spotify Integration**: Seamlessly fetch tracks from any public Spotify playlist
- 🧠 **AI-Powered Matching**: Advanced semantic search to find the best song matches
- 🔍 **Smart Scraping**: Intelligent web scraping from multiple music sources
- 📊 **Mood Analysis**: AI-powered playlist mood detection and analysis
- 📦 **Batch Download**: Download entire playlists as convenient ZIP files
- 🎨 **Beautiful UI**: Modern, responsive web interface
- ⚡ **Fast Processing**: Optimized for speed and reliability
- 🔧 **Easy Setup**: Simple installation and configuration

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Spotify Developer Account (for API access)
- Chrome/Chromium browser (for web scraping)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Pradheep-S/SonicSync.git
   cd SonicSync
   ```

2. **Run the setup script**
   
   **Linux/macOS:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   **Windows:**
   ```cmd
   setup.bat
   ```

3. **Configure Spotify API**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy your Client ID and Client Secret
   - Edit `.env` file and add your credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

4. **Start the application**
   ```bash
   python run.py
   ```

5. **Open your browser** and go to `http://localhost:5000`

## 🎯 How It Works

1. **Input**: Paste a Spotify playlist URL
2. **Analysis**: AI analyzes the playlist and extracts track information
3. **Matching**: Advanced algorithms find the best matching songs online
4. **Download**: Batch download all songs with intelligent retry logic
5. **Package**: Get your music as a convenient ZIP file

## 🧠 AI Components

### Semantic Matching
- Uses `sentence-transformers` for intelligent song matching
- Compares track names and artists using advanced NLP
- Handles variations in song titles and artist names

### Mood Analysis
- Analyzes playlist content to determine overall mood
- Provides confidence scores and detailed breakdowns
- Helps users understand their music preferences

### Query Enhancement
- Automatically cleans and optimizes search queries
- Removes noise words and formatting that could hurt search results
- Suggests alternative search terms when needed

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python) |
| **AI/ML** | sentence-transformers, PyTorch |
| **Web Scraping** | BeautifulSoup, Selenium |
| **Spotify API** | spotipy |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Packaging** | zipfile |

## 📁 Project Structure

```
SonicSync/
├── app.py                 # Main Flask application
├── run.py                 # Application runner
├── requirements.txt       # Python dependencies
├── utils.py              # Utility functions
├── setup.sh/setup.bat    # Setup scripts
├── services/             # Core services
│   ├── spotify_service.py    # Spotify API integration
│   ├── scraper_service.py    # Web scraping logic
│   ├── ai_service.py         # AI matching algorithms
│   └── download_service.py   # Download management
├── templates/            # HTML templates
│   ├── index.html           # Main page
│   └── error.html           # Error page
├── downloads/            # Downloaded files (auto-created)
├── temp/                # Temporary files (auto-created)
└── logs/                # Application logs (auto-created)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Optional: OpenAI API for enhanced AI features
OPENAI_API_KEY=your_openai_api_key

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development  # or production
```

### Application Settings

Key configuration options in `utils.py`:

- `max_file_size`: Maximum file size for downloads (100MB)
- `max_playlist_size`: Maximum tracks per playlist (500)
- `download_timeout`: Download timeout in seconds (30)
- `rate_limit_delay`: Delay between downloads (1 second)

## 📊 API Endpoints

### POST `/api/analyze`
Analyze a Spotify playlist and return track information.

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
  "mood_analysis": {
    "mood": "energetic",
    "confidence": 0.8,
    "description": "..."
  },
  "status": "success"
}
```

### POST `/api/download`
Download the entire playlist as a ZIP file.

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
  "zip_filename": "playlist_20231225_120000.zip"
}
```

### POST `/api/search`
Search for a single track.

**Request:**
```json
{
  "query": "Shape of You Ed Sheeran"
}
```

## 🚦 Usage Examples

### Basic Usage
1. Open SonicSync in your browser
2. Paste a Spotify playlist URL
3. Click "Analyze & Download"
4. Wait for processing to complete
5. Download your ZIP file

### Supported Playlist URLs
- `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- `spotify:playlist:37i9dQZF1DXcBWIGoYBM5M`
- Direct playlist ID: `37i9dQZF1DXcBWIGoYBM5M`

## 🔍 Troubleshooting

### Common Issues

1. **"No tracks found"**
   - Ensure the playlist is public
   - Check if the URL is correct
   - Verify Spotify API credentials

2. **Downloads failing**
   - Check internet connection
   - Ensure Chrome/Chromium is installed
   - Try with a smaller playlist first

3. **AI matching not working**
   - Install required AI packages: `pip install sentence-transformers torch`
   - Check available disk space
   - Restart the application

### Debug Mode

Enable debug mode by setting `FLASK_ENV=development` in your `.env` file.

## 📝 Legal Notice

**Important**: This tool is for educational purposes only. Please ensure you have the right to download and use any content. Respect copyright laws and terms of service of all platforms. The developers are not responsible for any misuse of this software.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for playlist data
- [sentence-transformers](https://www.sbert.net/) for AI matching capabilities
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the beautiful UI

## 📧 Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/Pradheep-S/SonicSync/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide detailed information about your setup and the issue

---

Made with ❤️ by [Pradheep](https://github.com/Pradheep-S)
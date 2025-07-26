@echo off
echo 🎵 Setting up SonicSync - AI Playlist Downloader

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing Python packages...
pip install -r requirements.txt

REM Create .env file from example
if not exist .env (
    echo 🔧 Creating .env file...
    copy .env.example .env
    echo ⚠️ Please edit .env file and add your Spotify API credentials
) else (
    echo ✅ .env file already exists
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist downloads mkdir downloads
if not exist temp mkdir temp
if not exist logs mkdir logs

echo.
echo 🎉 Setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit .env file and add your Spotify API credentials:
echo    - Go to https://developer.spotify.com/dashboard
echo    - Create a new app
echo    - Copy Client ID and Client Secret to .env file
echo.
echo 2. Install Chrome for web scraping (optional but recommended)
echo.
echo 3. Start the application:
echo    python run.py
echo.
echo 🌐 The app will be available at http://localhost:5000
pause

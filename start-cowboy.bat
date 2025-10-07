@echo off
title Basement Cowboy - AI News Aggregation Platform
color 0A

echo.
echo  ██████╗ ██████╗ ██╗    ██╗██████╗  ██████╗ ██╗   ██╗
echo ██╔════╝██╔═══██╗██║    ██║██╔══██╗██╔═══██╗╚██╗ ██╔╝
echo ██║     ██║   ██║██║ █╗ ██║██████╔╝██║   ██║ ╚████╔╝ 
echo ██║     ██║   ██║██║███╗██║██╔══██╗██║   ██║  ╚██╔╝  
echo ╚██████╗╚██████╔╝╚███╔███╔╝██████╔╝╚██████╔╝   ██║   
echo  ╚═════╝ ╚═════╝  ╚══╝╚══╝ ╚═════╝  ╚═════╝    ╚═╝   
echo.
echo                🤠 BASEMENT COWBOY 🤠
echo        AI-Powered News Aggregation Platform
echo.
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📥 Please install Python 3.8+ from: https://python.org
    echo    Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python detected: 
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip and install dependencies
echo 📥 Installing/updating dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Install Playwright browser
echo 🎭 Installing Playwright browser (this may take a moment)...
playwright install chromium --quiet
if errorlevel 1 (
    echo ⚠️  Warning: Playwright browser installation failed
    echo    News scraping may not work properly
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo ⚠️  Configuration file (.env) not found!
    echo 📝 Creating from template...
    copy ".env.template" ".env" >nul
    echo.
    echo ================================================================
    echo  🔧 CONFIGURATION REQUIRED
    echo ================================================================
    echo.
    echo Please edit the .env file with your configuration:
    echo.
    echo   1. Add your OpenAI API key (get from: https://platform.openai.com/api-keys)
    echo   2. Set a secure FLASK_SECRET_KEY
    echo   3. Set FLASK_DEBUG=False for production
    echo.
    echo The .env file has been created. Edit it and run this script again.
    echo.
    notepad .env
    echo.
    echo After editing the .env file, run this script again to start the application.
    pause
    exit /b 0
)

REM Check if OpenAI API key is configured
findstr /C:"OPENAI_API_KEY=your-openai-api-key-here" .env >nul
if not errorlevel 1 (
    echo.
    echo ⚠️  OpenAI API key not configured!
    echo.
    echo Please edit the .env file and add your actual OpenAI API key.
    echo Get your API key from: https://platform.openai.com/api-keys
    echo.
    notepad .env
    echo.
    echo After adding your API key, run this script again.
    pause
    exit /b 0
)

REM Set production environment variables
set FLASK_DEBUG=False
set FLASK_ENV=production

REM Start the application
echo.
echo ================================================================
echo  🚀 STARTING BASEMENT COWBOY
echo ================================================================
echo.
echo 🌟 Launching application...
echo 📱 Web interface will be available at: http://localhost:5000
echo.
echo 💡 Tips:
echo    - Use Ctrl+C to stop the application
echo    - Keep this window open while using the application
echo    - Access the web interface in your browser
echo.
echo ================================================================
echo.

python run.py

REM If we get here, the application has stopped
echo.
echo 🛑 Application stopped.
echo.
pause
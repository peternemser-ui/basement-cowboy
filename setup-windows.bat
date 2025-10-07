@echo off
echo.
echo =====================================================
echo   BASEMENT COWBOY - AUTOMATED WINDOWS INSTALLER
echo =====================================================
echo.
echo This script will automatically set up Basement Cowboy
echo on your Windows computer. Please wait...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH.
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
python --version

REM Check if we're in the right directory
if not exist "run.py" (
    echo ❌ ERROR: Please run this script from the basement-cowboy-before folder
    echo Make sure you have the complete project files!
    pause
    exit /b 1
)

echo ✅ Project files found!

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created!

REM Activate virtual environment and install dependencies
echo.
echo 📦 Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed!

REM Install Playwright browser
echo.
echo 🌐 Installing browser for web scraping...
playwright install chromium
if errorlevel 1 (
    echo ⚠️  WARNING: Browser installation failed, but continuing...
    echo You may need to install it manually later.
)

REM Setup environment file
echo.
echo ⚙️  Setting up configuration...
if not exist ".env" (
    if exist ".env.template" (
        copy ".env.template" ".env" >nul
        echo ✅ Environment file created from template
    ) else (
        echo # Basement Cowboy Environment Configuration > .env
        echo OPENAI_API_KEY=your-openai-api-key-here >> .env
        echo FLASK_SECRET_KEY=your-random-secret-key-here >> .env
        echo ✅ Basic environment file created
    )
) else (
    echo ✅ Environment file already exists
)

REM Create start script
echo.
echo 🚀 Creating startup script...
echo @echo off > start-basement-cowboy.bat
echo echo Starting Basement Cowboy... >> start-basement-cowboy.bat
echo call venv\Scripts\activate.bat >> start-basement-cowboy.bat
echo python run.py >> start-basement-cowboy.bat
echo pause >> start-basement-cowboy.bat

echo ✅ Startup script created!

REM Final instructions
echo.
echo =====================================================
echo           🎉 INSTALLATION COMPLETE! 🎉
echo =====================================================
echo.
echo NEXT STEPS:
echo.
echo 1. 🔑 Add your OpenAI API key to the .env file:
echo    - Open .env in notepad
echo    - Replace "your-openai-api-key-here" with your real API key
echo    - Get API key from: https://platform.openai.com
echo.
echo 2. 🚀 Run Basement Cowboy:
echo    - Double-click "start-basement-cowboy.bat"
echo    - OR run: python run.py
echo.
echo 3. 🌐 Open your browser to: http://localhost:5000
echo.
echo 📚 For more help, see QUICK_START.md
echo.
echo =====================================================
echo.

REM Ask if user wants to start now
set /p start_now="Start Basement Cowboy now? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo 🚀 Starting Basement Cowboy...
    echo.
    echo ⚠️  IMPORTANT: Add your OpenAI API key in the web interface!
    echo.
    timeout /t 3 /nobreak >nul
    python run.py
) else (
    echo.
    echo 👍 Setup complete! Run "start-basement-cowboy.bat" when ready.
)

pause
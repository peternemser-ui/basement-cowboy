# Production Start Script
# This script starts the Basement Cowboy application in production mode

Write-Host "🚀 Starting Basement Cowboy in Production Mode" -ForegroundColor Green

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.template" ".env"
    Write-Host "📝 Please edit .env file with your configuration before starting." -ForegroundColor Yellow
    return
}

# Set production environment
$env:FLASK_DEBUG = "False"
$env:FLASK_ENV = "production"

# Start the application
Write-Host "🌟 Starting Basement Cowboy application..." -ForegroundColor Green
Write-Host "📱 Access the application at: http://localhost:5000" -ForegroundColor Cyan

python run.py
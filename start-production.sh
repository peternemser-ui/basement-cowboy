#!/bin/bash
# Production Setup and Start Script for Linux/Mac

echo "🚀 Setting up Basement Cowboy for Production"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright
echo "🎭 Installing Playwright browser..."
playwright install chromium

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your configuration:"
    echo "   - Add your OpenAI API key"
    echo "   - Set secure FLASK_SECRET_KEY"
    echo "   - Set FLASK_DEBUG=False for production"
    echo ""
    echo "Then run this script again to start the application."
    exit 0
fi

# Set production environment
export FLASK_DEBUG=False
export FLASK_ENV=production

# Start the application
echo "🌟 Starting Basement Cowboy application..."
echo "📱 Access the application at: http://localhost:5000"
echo ""

python run.py
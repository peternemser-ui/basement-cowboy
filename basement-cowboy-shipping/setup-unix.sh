#!/bin/bash

echo ""
echo "====================================================="
echo "   BASEMENT COWBOY - AUTOMATED UNIX INSTALLER"
echo "====================================================="
echo ""
echo "This script will automatically set up Basement Cowboy"
echo "on your Mac/Linux computer. Please wait..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
}

print_info() {
    echo -e "${BLUE}📦 $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    echo ""
    echo "Please install Python 3:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo ""
    exit 1
fi

print_success "Python found!"
python3 --version

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    print_error "Please run this script from the basement-cowboy-before folder"
    echo "Make sure you have the complete project files!"
    exit 1
fi

print_success "Project files found!"

# Create virtual environment
echo ""
print_info "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

print_success "Virtual environment created!"

# Activate virtual environment and install dependencies
echo ""
print_info "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi

print_success "Dependencies installed!"

# Install Playwright browser
echo ""
print_info "Installing browser for web scraping..."
playwright install chromium
if [ $? -ne 0 ]; then
    print_warning "Browser installation failed, but continuing..."
    echo "You may need to install it manually later."
fi

# Setup environment file
echo ""
print_info "Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        cp ".env.template" ".env"
        print_success "Environment file created from template"
    else
        cat > .env << EOF
# Basement Cowboy Environment Configuration
OPENAI_API_KEY=your-openai-api-key-here
FLASK_SECRET_KEY=your-random-secret-key-here
EOF
        print_success "Basic environment file created"
    fi
else
    print_success "Environment file already exists"
fi

# Create start script
echo ""
print_info "Creating startup script..."
cat > start-basement-cowboy.sh << 'EOF'
#!/bin/bash
echo "Starting Basement Cowboy..."
cd "$(dirname "$0")"
source venv/bin/activate
python run.py
EOF

chmod +x start-basement-cowboy.sh
print_success "Startup script created!"

# Final instructions
echo ""
echo "====================================================="
echo -e "           ${GREEN}🎉 INSTALLATION COMPLETE! 🎉${NC}"
echo "====================================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo -e "${BLUE}1. 🔑 Add your OpenAI API key to the .env file:${NC}"
echo "   - Edit .env file: nano .env (or your preferred editor)"
echo "   - Replace 'your-openai-api-key-here' with your real API key"
echo "   - Get API key from: https://platform.openai.com"
echo ""
echo -e "${BLUE}2. 🚀 Run Basement Cowboy:${NC}"
echo "   - Run: ./start-basement-cowboy.sh"
echo "   - OR run: source venv/bin/activate && python run.py"
echo ""
echo -e "${BLUE}3. 🌐 Open your browser to: http://localhost:5000${NC}"
echo ""
echo -e "${BLUE}📚 For more help, see QUICK_START.md${NC}"
echo ""
echo "====================================================="
echo ""

# Ask if user wants to start now
echo -n "Start Basement Cowboy now? (y/n): "
read -r start_now
if [[ $start_now =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting Basement Cowboy..."
    echo ""
    echo "⚠️  IMPORTANT: Add your OpenAI API key in the web interface!"
    echo ""
    sleep 3
    python run.py
else
    echo ""
    echo "👍 Setup complete! Run './start-basement-cowboy.sh' when ready."
fi
# 🚀 Basement Cowboy - Quick Setup Guide

Welcome to **Basement Cowboy**, an AI-powered news aggregation platform! This guide will get you up and running in minutes.

## 📋 System Requirements

- **Python 3.8+** (recommended: Python 3.11)
- **Windows 10/11**, **macOS**, or **Linux**
- **8GB RAM** (minimum), 16GB recommended
- **2GB free disk space**
- **Internet connection** for news scraping and AI features

## 🎯 One-Click Installation

### Windows Users
1. **Download** this entire folder
2. **Double-click** `setup-windows.bat`
3. **Follow the prompts** - the script will handle everything!

### Mac/Linux Users
1. **Download** this entire folder
2. **Open Terminal** in this folder
3. **Run:** `chmod +x setup-unix.sh && ./setup-unix.sh`

## 🔧 Manual Installation (if needed)

### Step 1: Install Python
- **Windows:** Download from [python.org](https://python.org) (check "Add to PATH")
- **Mac:** `brew install python3` or download from python.org
- **Linux:** `sudo apt install python3 python3-pip python3-venv`

### Step 2: Setup Environment
```bash
# Clone or download the project
cd basement-cowboy-before

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser for scraping
playwright install chromium
```

### Step 3: Configure API Keys
1. **Copy** `.env.template` to `.env`
2. **Add your OpenAI API key:**
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   FLASK_SECRET_KEY=your-random-secret-key
   ```

### Step 4: Run the Application
```bash
python run.py
```

Visit: **http://localhost:5000**

## 🔑 Getting API Keys

### OpenAI API Key (Required for AI Features)
1. Visit: [platform.openai.com](https://platform.openai.com)
2. Sign up/Login
3. Go to **API Keys** section
4. Create new secret key
5. Copy the key (starts with `sk-proj-`)

**Cost:** ~$1-5 per month for typical usage

### WordPress Integration (Optional)
1. Edit `config/wordpress_config.json`
2. Add your WordPress site details
3. Use **Application Passwords** (not main password)

## 🚀 Quick Start Guide

1. **Start the app:** `python run.py`
2. **Open browser:** http://localhost:5000
3. **Enter OpenAI API key** when prompted
4. **Click "Regenerate Scraper"** to collect news
5. **Review articles** and use AI features
6. **Publish to WordPress** (if configured)

## 📁 Project Structure

```
basement-cowboy-before/
├── 🔧 setup-windows.bat     # Windows auto-installer
├── 🔧 setup-unix.sh         # Mac/Linux auto-installer  
├── 🐍 run.py                # Main application launcher
├── 📝 requirements.txt      # Python dependencies
├── ⚙️ .env.template         # Environment variables template
├── 📂 app/                  # Flask web application
├── 📂 scraper/              # News scraping engine
├── 📂 config/               # Configuration files
├── 📂 output/               # Generated articles and data
├── 📂 static/               # Web assets (CSS, JS, images)
└── 📂 templates/            # HTML templates
```

## 🛠️ Features Overview

### Core Features
- **🕷️ News Scraping:** Collects articles from 180+ news sources
- **🤖 AI Summarization:** Generates concise summaries using OpenAI
- **🎨 AI Image Generation:** Creates relevant images with DALL-E
- **📊 Article Management:** Review, filter, and organize content
- **🌐 WordPress Publishing:** Direct integration with WordPress sites

### Advanced Features
- **📈 Progress Tracking:** Real-time scraping progress
- **🔄 Auto-refresh:** Continuous content updates
- **📱 Responsive Design:** Works on desktop, tablet, mobile
- **⚡ High Performance:** Handles thousands of articles
- **🔒 Secure:** Environment-based configuration

## 🆘 Troubleshooting

### Common Issues

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**"Permission denied" error:**
```bash
# Windows (run as Administrator)
# Mac/Linux:
sudo chmod +x setup-unix.sh
```

**OpenAI API errors:**
- Check your API key format (starts with `sk-proj-`)
- Verify you have credits in your OpenAI account
- Check internet connection

**Scraping issues:**
- Some sites may block automated access
- Try running again later
- Check your internet connection

**Port already in use:**
```bash
# Find and kill the process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

## 📞 Support

### Getting Help
1. **Check this README** for common solutions
2. **Check the logs** in the terminal for error messages
3. **Verify your .env file** has correct API keys
4. **Try restarting** the application

### System Status Check
Run the built-in diagnostics:
```bash
python -c "from app.routes import test_environment; test_environment()"
```

## 🎯 Production Deployment

For production deployment, see:
- `PRODUCTION_GUIDE.md` - Full production setup
- `DEPLOYMENT_GUIDE.md` - Server deployment options
- `docker-compose.yml` - Docker containerization

## 📄 License & Credits

**Basement Cowboy** - AI-Powered News Aggregation Platform
- Built with Flask, OpenAI, and modern web technologies
- Uses Playwright for robust web scraping
- Bootstrap 5 for responsive UI design

## 🎉 You're Ready!

Once everything is set up:
1. **Run:** `python run.py`
2. **Visit:** http://localhost:5000
3. **Enter your OpenAI API key**
4. **Start scraping news!**

**Enjoy your AI-powered news aggregation platform!** 🚀
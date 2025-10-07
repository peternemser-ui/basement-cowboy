# 🤠 Basement Cowboy - User Distribution Package

**Basement Cowboy** is an AI-powered news aggregation platform that automatically scrapes news articles, enhances them with artificial intelligence, and publishes them to WordPress websites.

## 📦 What's Included

This distribution package contains everything you need to run Basement Cowboy:

- **Automated Setup Scripts** - One-click installation for Windows, Mac, and Linux
- **Complete Source Code** - Full Flask application and scraper modules  
- **System Checker** - Validates your environment before running
- **Documentation** - Comprehensive guides and troubleshooting
- **Configuration Templates** - Easy setup for API keys and WordPress

## 🚀 Quick Start (5 Minutes)

### Step 1: Run Setup Script

**Windows Users:**
```cmd
# Double-click setup-windows.bat
# OR run in Command Prompt:
setup-windows.bat
```

**Mac/Linux Users:**
```bash
# Make executable and run:
chmod +x setup-unix.sh
./setup-unix.sh
```

### Step 2: Configure API Keys

1. Copy `.env.template` to `.env`
2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   FLASK_SECRET_KEY=your-random-32-char-secret
   ```

### Step 3: Run System Check

```bash
python system_check.py
```

### Step 4: Start Application

```bash
python run.py
```

### Step 5: Open Browser

Navigate to: `http://localhost:5000`

## 📋 System Requirements

- **Python 3.8 or higher**
- **Internet connection** (for news scraping and AI features)
- **2GB RAM minimum** (4GB recommended)
- **1GB free disk space**
- **OpenAI API account** (for AI features)

## 🛠️ What the Setup Scripts Do

The automated setup scripts will:

1. ✅ **Check Python installation** (install if missing on some systems)
2. ✅ **Create virtual environment** (isolated Python environment)
3. ✅ **Install all dependencies** (Flask, OpenAI, BeautifulSoup, etc.)
4. ✅ **Setup Playwright browser** (for dynamic web scraping)
5. ✅ **Create configuration files** (templates for easy setup)
6. ✅ **Validate installation** (run system checks)
7. ✅ **Display next steps** (how to configure and run)

## 📁 File Structure

```
basement-cowboy/
├── run.py                    # Main application entry point
├── system_check.py          # Environment validation tool
├── setup-windows.bat        # Windows setup script
├── setup-unix.sh           # Mac/Linux setup script
├── requirements.txt         # Python dependencies
├── .env.template           # Environment configuration template
├── QUICK_START.md          # Detailed setup guide
├── app/                    # Flask web application
├── scraper/               # News scraping modules
├── config/                # Configuration files
├── output/               # Generated news articles and logs
└── docs/                 # Additional documentation
```

## 🔧 Manual Installation (Advanced Users)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browser
playwright install chromium

# 5. Configure environment
cp .env.template .env
# Edit .env with your API keys

# 6. Run system check
python system_check.py

# 7. Start application
python run.py
```

## 🌐 Getting API Keys

### OpenAI API Key (Required)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create account or log in
3. Navigate to API Keys section
4. Create new secret key
5. Copy key (starts with `sk-proj-` or `sk-`)
6. Add to `.env` file

### WordPress Configuration (Optional)

If you want to publish to WordPress:

1. Go to your WordPress admin panel
2. Users → Profile → Application Passwords
3. Create new application password
4. Edit `config/wordpress_config.json`
5. Add your site URL, username, and application password

## 🎯 How It Works

1. **Scrape News** - Automatically crawls 180+ news websites
2. **AI Enhancement** - Uses OpenAI to categorize and summarize articles
3. **Human Review** - Web interface for selecting and editing articles
4. **WordPress Publishing** - Automatically formats and publishes content

## 📞 Getting Help

### First Steps
1. **Run system check:** `python system_check.py`
2. **Check the logs** in the terminal
3. **Verify .env configuration** has correct API keys
4. **Read QUICK_START.md** for detailed troubleshooting

### Common Issues

**Python not found:**
- Install Python 3.8+ from python.org
- Ensure Python is in your system PATH

**Permission denied (Mac/Linux):**
```bash
chmod +x setup-unix.sh
```

**Virtual environment issues:**
```bash
# Remove old environment and recreate
rm -rf venv
python -m venv venv
```

**Package installation fails:**
```bash
# Update pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Support Resources

- 📖 **QUICK_START.md** - Comprehensive setup guide
- 🔧 **TECHNICAL_BRIEF.md** - Technical documentation
- ✅ **SHIPPING_CHECKLIST.md** - Deployment checklist
- 🏭 **PRODUCTION_GUIDE.md** - Production deployment guide

## 🎉 Success!

Once setup is complete, you'll have a fully functional news aggregation platform that can:

- Automatically scrape news from hundreds of sources
- Use AI to enhance and categorize content
- Provide a beautiful web interface for content management
- Publish directly to WordPress websites
- Generate SEO-optimized content automatically

**Happy news aggregating! 🤠📰**

---

*Basement Cowboy v1.0.0 - AI-Powered News Aggregation Platform*
# Basement Cowboy - Setup and Run Guide

**Version:** 1.0  
**Date:** August 9, 2025  
**Target Audience:** Developers setting up the POC for the first time

---

## Overview

Basement Cowboy is a proof-of-concept automated news aggregation platform that scrapes 180+ news sources, enhances content with AI, and publishes to WordPress. This guide covers complete setup from scratch.

---

## Prerequisites

### System Requirements
- **OS:** Windows 10+, macOS 10.15+, or Ubuntu 18.04+
- **Python:** 3.11 or higher (3.13 recommended)
- **RAM:** Minimum 8GB
- **Storage:** 20GB free space
- **Network:** Stable broadband connection

### Required Accounts & API Keys
1. **OpenAI Account**
   - Sign up at https://platform.openai.com
   - Generate API key with GPT-3.5/4 and DALL-E access
   - Ensure billing is set up (typical daily cost: $5-15)

2. **WordPress Site**
   - Must have admin access
   - WordPress 5.0+ with REST API enabled
   - Application password configured (see WordPress Setup section)

---

## Installation Steps

### 1. Clone/Extract Codebase
```bash
# If from zip file (bc-codebase.zip)
unzip bc-codebase.zip
cd basement-cowboy

# If from repository
git clone [repository-url]
cd basement-cowboy
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (for dynamic scraping)
playwright install chromium

# Verify installations
python -c "import flask, openai, playwright, requests, beautifulsoup4; print('All packages installed successfully')"
```

### 4. Environment Configuration

Create `.env` file in the project root:
```bash
# Copy template
cp .env.example .env

# Edit with your values
OPENAI_API_KEY=sk-proj-your-actual-key-here
DALL_E_MODEL=dall-e-3
IMAGE_SIZE=1024x1024
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ Important:** Never commit the `.env` file to version control!

### 5. WordPress Configuration

#### Step 5a: Generate Application Password
1. Log into your WordPress admin dashboard
2. Go to **Users → Profile**
3. Scroll to **Application Passwords** section
4. Enter name: "Basement Cowboy API"
5. Click **Add New Application Password**
6. Copy the generated password (format: `xxxx xxxx xxxx xxxx`)

#### Step 5b: Configure WordPress Settings
Edit `config/wordpress_config.json`:
```json
{
  "wordpress_url": "https://your-site.com",
  "username": "your-wp-username",
  "application_password": "your-app-password-here"
}
```

#### Step 5c: Verify WordPress API Access
```bash
# Test API connection
curl -u "username:app-password" "https://your-site.com/wp-json/wp/v2/posts?per_page=1"
```

### 6. News Sources Configuration

The system comes with 180+ pre-configured news sources in `config/top_100_news_sites.txt`. No changes needed for initial testing.

To add sources later:
```bash
# Edit the file
nano config/top_100_news_sites.txt

# Add one URL per line
https://new-news-site.com
```

### 7. Verify Installation

```bash
# Check Python environment
python --version  # Should be 3.11+

# Test core imports
python -c "
import flask, openai, requests, beautifulsoup4
from playwright.sync_api import sync_playwright
print('✅ All core dependencies working')
"

# Check file structure
ls -la config/
# Should show: categories.json, wordpress_config.json, top_100_news_sites.txt

# Verify environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
assert os.getenv('OPENAI_API_KEY'), 'OpenAI API key not found'
assert os.getenv('FLASK_SECRET_KEY'), 'Flask secret key not found'
print('✅ Environment variables configured')
"
```

---

## Running the System

### 1. Start the Web Application

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Start Flask app
python run.py
```

**Expected Output:**
```
2025-08-09 08:41:59,423 - INFO - Loaded WP config -> URL:https://your-site.com, user:your-username
 * Serving Flask app 'app.routes'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### 2. Access Web Interface

Open browser and navigate to: **http://127.0.0.1:5000**

You should see the "Basement Cowboy News Command Center" dashboard.

### 3. Run Initial Scraping

#### Option A: Via Web Interface
1. Click **"Regenerate Scraper"** button on dashboard
2. Monitor progress in browser
3. Wait 15-30 minutes for completion

#### Option B: Via Command Line
```bash
# Open new terminal (keep Flask running)
cd basement-cowboy
source venv/bin/activate  # Activate environment

# Run scraper directly
python scraper/scrape_news.py
```

### 4. Verify Scraping Results

```bash
# Check output directory
ls -la output/news_articles/

# Should show files like:
# news_articles_2025-08-09-1.json
# news_articles_2025-08-09-2.json

# Check article count
python -c "
import json
with open('output/news_articles/news_articles_2025-08-09-1.json') as f:
    articles = json.load(f)
    print(f'✅ Scraped {len(articles)} articles')
"
```

### 5. Test AI Enhancement

1. Go to web interface: http://127.0.0.1:5000
2. Select some articles (checkboxes)
3. Click **"Review Selected Articles"**
4. On details page, click **"Generate Summary"** for an article
5. Verify AI-generated summary appears

### 6. Test WordPress Publishing

1. On article details page, check **"Publish"** for selected articles
2. Choose appropriate categories
3. Click **"Publish to basementcowboy.com"**
4. Verify success message
5. Check your WordPress site for published posts

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Symptom: ModuleNotFoundError
# Solution: Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. OpenAI API Errors
```bash
# Symptom: "Invalid API key" or rate limit errors
# Check API key
python -c "
import openai, os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('✅ OpenAI API key valid')
"

# Check billing
# Go to https://platform.openai.com/account/billing
```

#### 3. WordPress Connection Errors
```bash
# Symptom: 401 Unauthorized or connection failures
# Test manually
curl -u "username:app-password" "https://your-site.com/wp-json/wp/v2/posts?per_page=1"

# Common fixes:
# - Verify application password is correct
# - Check WordPress REST API is enabled
# - Verify site URL in config
```

#### 4. Scraping Failures
```bash
# Symptom: No articles scraped or many errors
# Check network connection
ping google.com

# Test single source
python -c "
import requests
r = requests.get('https://bbc.com/news')
print(f'Status: {r.status_code}')
"

# Common fixes:
# - Check internet connection
# - Some sites may block automated requests (expected)
# - Verify news sources list is accessible
```

#### 5. Playwright Browser Issues
```bash
# Symptom: Browser launch failures
# Reinstall browsers
playwright install chromium

# For headless server environments
playwright install --with-deps chromium
```

### Performance Optimization

#### 1. Reduce Scraping Load
Edit `config/top_100_news_sites.txt` and comment out slow sources:
```bash
# https://slow-site.com  # Comment out problematic sources
```

#### 2. Adjust AI Costs
Modify AI usage in `app/routes.py`:
- Use gpt-3.5-turbo instead of gpt-4 for cost savings
- Reduce max_tokens for summaries
- Cache AI responses to avoid duplicate calls

#### 3. Database Migration (Future)
Current POC uses JSON files. For production:
- Migrate to PostgreSQL or MongoDB
- Implement proper caching with Redis
- Add background task queue (Celery)

### Logging and Debugging

#### Enable Verbose Logging
Edit `scraper/scrape_news.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose output
```

#### Check Log Files
```bash
# Application logs
tail -f output/logs/scraper.log

# Flask debug output
# Available in terminal where you run `python run.py`
```

#### Monitor API Usage
- **OpenAI:** https://platform.openai.com/usage
- **WordPress:** Check your site's admin logs

---

## File Structure Reference

```
basement-cowboy/
├── run.py                    # Main application entry
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables (create this)
├── .env.example            # Template for .env
├── app/
│   ├── routes.py           # Flask routes and business logic
│   ├── __init__.py         # Flask app initialization
│   ├── templates/          # HTML templates
│   │   ├── review.html     # Main dashboard
│   │   └── details.html    # Article editing
│   └── static/             # CSS, JS, images
├── scraper/
│   ├── scrape_news.py      # Main scraping script
│   ├── dynamic_scraper.py  # Playwright integration
│   └── ai_enhancements.py  # AI processing
├── config/
│   ├── wordpress_config.json     # WP credentials
│   ├── categories.json           # Article categories
│   └── top_100_news_sites.txt   # News sources list
└── output/
    ├── news_articles/       # Scraped articles (JSON)
    └── logs/               # Application logs
```

---

## Security Notes

1. **Never commit sensitive files:**
   - `.env` (contains API keys)
   - `config/wordpress_config.json` (contains passwords)

2. **API Key Management:**
   - Rotate OpenAI keys monthly
   - Monitor usage for unexpected spikes
   - Use separate keys for dev/prod

3. **WordPress Security:**
   - Use application passwords (not main password)
   - Regularly review WordPress user permissions
   - Monitor for unauthorized posts

---

## Next Steps

After successful POC validation:
1. **Performance Testing:** Run multiple scraping cycles
2. **Content Quality Review:** Evaluate AI-generated summaries
3. **WordPress Integration Testing:** Verify publishing workflow
4. **Documentation Updates:** Note any issues or improvements
5. **UI Enhancement Planning:** Prepare for Phase 2 development

---

## Support

For technical issues:
1. Check this troubleshooting guide first
2. Review log files in `output/logs/`
3. Test individual components (scraper, AI, WordPress) separately
4. Document any new issues for team review

**Setup Complete!** You should now have a fully functional Basement Cowboy instance.

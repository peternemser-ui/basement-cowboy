# Setup Guide

This guide walks you through setting up Basement Cowboy for development or production use.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning)
- Docker (optional, for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/basement-cowboy.git
cd basement-cowboy
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Setup Wizard

```bash
python scripts/setup_wizard.py
```

This interactive wizard will:
- Check your Python version
- Verify required dependencies
- Create necessary directories
- Configure OpenAI API key
- Configure WordPress integration
- Generate environment files

### 5. Start the Application

```bash
python run.py
```

Access the web interface at: http://localhost:5000

## Manual Configuration

If you prefer manual setup, create a `.env` file:

```env
# Flask Settings
FLASK_DEBUG=false
SECRET_KEY=your-secret-key-here

# OpenAI Settings
OPENAI_API_KEY=sk-your-api-key

# WordPress Settings
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_PASSWORD=your-app-password

# Scraper Settings
SCRAPER_MAX_ARTICLES=100
SCRAPER_DELAY=1.0
```

## Docker Deployment

### Using Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables for Docker

Create a `.env` file or pass environment variables to docker-compose:

```yaml
# docker-compose.yml
services:
  app:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WORDPRESS_URL=${WORDPRESS_URL}
      - WORDPRESS_USERNAME=${WORDPRESS_USERNAME}
      - WORDPRESS_PASSWORD=${WORDPRESS_PASSWORD}
```

## WordPress Setup

### 1. Install Required Plugins

For full functionality, install these WordPress plugins:
- **WPGraphQL** - Enables GraphQL API
- **Application Passwords** - For secure API authentication

### 2. Create Application Password

1. Go to WordPress Admin → Users → Your Profile
2. Scroll to "Application Passwords"
3. Enter a name (e.g., "Basement Cowboy")
4. Click "Add New Application Password"
5. Copy the generated password

### 3. Configure in Basement Cowboy

Enter the application password in the setup wizard or `.env` file.

## OpenAI Setup

### 1. Get API Key

1. Go to https://platform.openai.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new secret key

### 2. Set Usage Limits (Recommended)

In OpenAI dashboard:
1. Go to Settings → Limits
2. Set monthly budget limit
3. Configure usage alerts

### 3. Configure in Basement Cowboy

Enter the API key in the setup wizard or `.env` file.

## Directory Structure

After setup, your directory should look like:

```
basement-cowboy/
├── app/                 # Flask application
├── config/              # Configuration files
├── data/                # Data files
├── output/              # Generated content
│   ├── news_articles/   # Scraped articles
│   ├── wordpress-output/ # Publishing logs
│   ├── logs/            # Application logs
│   └── cache/           # Cache files
├── scraper/             # Scraping modules
├── scripts/             # CLI utilities
├── tests/               # Test suite
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── run.py               # Application entry point
```

## Troubleshooting

### Common Issues

**Module not found errors:**
```bash
pip install -r requirements.txt
```

**Permission errors on Linux/macOS:**
```bash
chmod +x scripts/*.py
```

**Playwright not working:**
```bash
playwright install chromium
```

**WordPress connection fails:**
- Verify URL includes protocol (https://)
- Check Application Password is correct
- Ensure WordPress REST API is enabled

**OpenAI errors:**
- Verify API key is valid
- Check API usage limits
- Ensure sufficient account balance

### Getting Help

- Check the [FAQ](./FAQ.md)
- Review [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Open an issue on GitHub

## Next Steps

After setup:
1. Configure news sources in `config/top_100_news_sites.txt`
2. Customize categories in `config/categories.json`
3. Run your first scrape from the web interface
4. Review and publish articles to WordPress

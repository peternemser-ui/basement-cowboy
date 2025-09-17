# Basement Cowboy News Aggregation System

**Basement Cowboy** is an automated AI-powered news aggregation platform that scrapes news articles, enhances them with OpenAI, and publishes to WordPress. This system demonstrates a complete pipeline from news collection to publication with Cloudflare bypass and dual API support.

## 🚀 Quick Start

### Automated Setup
```bash
python setup.py
```

### Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Configure environment
cp .env.template .env
cp config/wordpress_config.json.template config/wordpress_config.json

# 3. Edit configuration files with your credentials
# 4. Run the application
python run.py
```

## 📋 Requirements

- **Python 3.8+**
- **OpenAI API Key** (entered through web interface)
- **WordPress Site** with Application Passwords enabled
- **Optional**: WPGraphQL plugin (for GraphQL API)

## ⚙️ Configuration

### Environment Variables (.env)
```env
FLASK_SECRET_KEY=your-random-32-character-secret-key
FLASK_DEBUG=True
```

**Note**: OpenAI API key is now entered through the secure web interface and stored in browser sessions only.

### WordPress Configuration (config/wordpress_config.json)
```json
{
  "wordpress_url": "https://your-site.com",
  "username": "your-wp-username", 
  "application_password": "xxxx xxxx xxxx xxxx xxxx xxxx",
  "api_version": "rest"
}
```

## 🏗️ Architecture

### Data Flow
```
News Sources → Scraper → JSON Files → Flask UI → AI Enhancement → WordPress Publishing
```

### Key Components
- **Entry Point**: `run.py` → `app/routes.py`
- **Scraper**: `scraper/main.py` with modules for fetching, parsing, and filtering
- **Frontend**: Bootstrap 5.3 templates with vanilla JavaScript
- **WordPress APIs**: Both REST API and GraphQL support

## 🔧 WordPress Publishing

### REST API (Default)
- Uses WordPress REST API v2 (`/wp-json/wp/v2/posts`)
- Authentication via Application Passwords
- Enhanced Cloudflare bypass with session management
- Browser-like headers to avoid bot detection

### GraphQL (Optional)
- Requires WPGraphQL plugin installation
- Set `"api_version": "graphql"` in config
- Install GraphQL dependencies: `pip install gql[all] graphql-core`

## 🌐 Cloudflare Bypass

The system includes sophisticated Cloudflare bypass mechanisms:

- **Session-based requests** with cookie persistence
- **Browser-like User-Agent headers** 
- **Site warmup requests** before API calls
- **Rate limiting protection** with delays
- **Comprehensive error handling**

## 📁 Project Structure

```
basement-cowboy/
├── app/                    # Flask application
│   ├── routes.py          # Main application routes
│   ├── wordpress_graphql.py  # GraphQL client
│   ├── templates/         # HTML templates
│   └── static/           # CSS/JS assets
├── scraper/              # News scraping modules
│   ├── main.py           # Scraper entry point
│   ├── fetch_page.py     # Web scraping
│   ├── parse_articles.py # Content parsing
│   └── filter_articles.py # Content filtering
├── config/               # Configuration files
│   ├── wordpress_config.json # WordPress settings
│   ├── categories.json   # News categories
│   └── top_100_news_sites.txt # News sources
├── output/               # Generated content
│   ├── news_articles/    # Scraped news JSON
│   └── wordpress-output/ # Publishing results
├── tests/                # Test scripts
├── requirements.txt      # Python dependencies
├── setup.py             # Automated setup script
└── run.py               # Application entry point
```

## 🎯 Usage

### 1. Start the Application
```bash
python run.py
```
Access at: http://127.0.0.1:5000

### 2. Enter OpenAI API Key
- Beautiful web interface for secure API key entry
- Real-time validation with OpenAI API
- Session-based storage (never saved to disk)
- Logout functionality to clear API key

### 3. Scrape News Articles
- Click "Regenerate Scraper" in the web interface
- Real-time progress tracking with auto-refresh
- Articles saved to `output/news_articles/` with proper chronological sorting
- Newest scraping sessions appear first in file selector

### 4. Review and Select Articles
- Grid view of scraped articles with images
- Select at least 50 articles for publishing
- File dropdown shows newest sessions first
- Counter tracks progress toward publication goal

### 5. Enhance with AI
- Navigate to details page for selected articles
- Add OpenAI-generated summaries and images
- Customize content before publishing
- Validate titles with AI assistance

### 6. Publish to WordPress
- Review final enhanced content
- Bulk publish selected articles
- Articles include structured JSON data for themes
- Real-time publishing progress and results

## 🔬 Testing

The system includes comprehensive test scripts in the `tests/` directory:

- `test_cloudflare_bypass.py` - Test Cloudflare bypass methods
- `test_wordpress_connection.py` - Test WordPress API connectivity  
- `test_graphql_wordpress.py` - Test GraphQL functionality
- `test_environment.py` - Validate environment setup

## 🛠️ Development

### Debug Mode
Set `FLASK_DEBUG=True` in `.env` for development with:
- Auto-reload on file changes
- Detailed error pages
- Debug toolbar

### Adding News Sources
Edit `config/top_100_news_sites.txt` to add new news sources.

### Customizing Categories
Modify `config/categories.json` to change article categorization.

## 🔒 Security Features

- **Session-based API key management** (no environment variables)
- **Application Password authentication** (not main WordPress password)
- **Secure API key entry** through web interface only
- **Input sanitization** for all user content
- **AI content filtering** for inappropriate content
- **Rate limiting** to avoid being blocked
- **Logout functionality** to clear sensitive session data

## 📊 Content Format

Published articles include:
- **HTML content** for display
- **Embedded JSON data** in structured format
- **CSS styling** for responsive design
- **Image integration** with proper alt tags
- **Category organization** 
- **Metadata** for theme consumption

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. See license file for details.

## 🆘 Troubleshooting

### Common Issues

**Cloudflare 403 Errors**
- Ensure WordPress Application Passwords are enabled
- Check that User-Agent headers are browser-like
- Verify site warmup is working

**GraphQL Import Errors**
- Install GraphQL dependencies: `pip install gql[all] graphql-core`
- Ensure WPGraphQL plugin is installed on WordPress

**Scraping Failures** 
- Check anti-bot measures on target sites
- Verify Playwright browser installation
- Review User-Agent rotation settings

**WordPress Publishing Fails**
- Verify Application Password format (spaces included)
- Check WordPress user permissions
- Test REST API endpoint manually

### Support

For issues and questions:
1. Check the test scripts in `tests/` directory
2. Review logs for detailed error information
3. Verify configuration files are properly formatted
4. Test individual components separately

# Basement Cowboy AI Assistant Guide

**Basement Cowboy** is an automated AI-powered news aggregation platform that scrapes news articles, enhances them with OpenAI, and publishes to WordPress. This POC demonstrates a complete pipeline from news collection to publication.

## Core Architecture

### Big Picture Data Flow
```
News Sources → Scraper → JSON Files → Flask UI → AI Enhancement → WordPress Publishing
```

The system operates in distinct phases:
1. **Scraping**: `scraper/scrape_news.py` crawls 180+ news sites, saves to `output/news_articles/`
2. **Review**: Flask app loads JSON files, presents articles for human curation
3. **Enhancement**: AI summarizes content and generates images via OpenAI APIs
4. **Publishing**: Structured JSON embedded in WordPress posts for theme consumption

### Key Components
- **Entry Point**: `run.py` → `app/routes.py` (Flask factory pattern)
- **Scraper**: `scraper/main.py` + modules (`fetch_page.py`, `parse_articles.py`, `filter_articles.py`)
- **Frontend**: Bootstrap 5.3 templates in `app/templates/` with vanilla JS in `app/static/`
- **Configuration**: JSON files in `config/` (categories, WordPress creds, news sources)

## Critical Development Workflows

### Environment Setup
```bash
# Virtual environment is essential
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install chromium  # For dynamic scraping
```

### Configuration Requirements
1. **`.env` file** (never commit):
   ```
   OPENAI_API_KEY=sk-proj-...
   FLASK_SECRET_KEY=random-32-char-string
   ```

2. **`config/wordpress_config.json`** (application passwords, not main WP password):
   ```json
   {
     "wordpress_url": "https://site.com",
     "username": "wp-user",
     "application_password": "xxxx xxxx xxxx xxxx"
   }
   ```

### Running the System
```bash
# Start Flask development server
python run.py

# Trigger news scraping (from web UI or directly)
python scraper/scrape_news.py

# Test individual components
python test_scraper.py        # Debug single site scraping
python test_environment.py    # Validate setup
python test_openai.py        # Test AI integration
```

## Project-Specific Patterns

### File-Based Data Persistence
- **No database** - articles stored as timestamped JSON files in `output/news_articles/`
- **Daily sessions**: `news_articles_2025-09-13-1.json`, `news_articles_2025-09-13-2.json`
- **Load pattern**: Frontend always loads most recent file by default

### OpenAI Integration Conventions
- **Dual API key support**: Environment variable OR session-stored key for runtime validation
- **Safety filtering**: Extensive blocked word lists for image generation prompts
- **Fallback chains**: Multiple OpenAI client instantiation methods (SDK → legacy → HTTP)
- **Debug artifacts**: Error responses saved to `debug_generate_image_error.json`

### WordPress Publishing Pattern
- **Structured JSON embedding**: Articles embedded as JSON in `<pre id="structured-json">` tags
- **Bulk publishing**: Multiple articles combined into single WordPress post
- **Media handling**: AI-generated images uploaded to WordPress media library first
- **Authentication**: Base64-encoded application passwords in headers

### UI State Management
- **Session-based**: OpenAI API keys stored in Flask sessions for validation
- **Prompt persistence**: User-entered prompts saved to `data/prompts.json`
- **Real-time feedback**: Server-sent events for long-running scraper operations

## Integration Points & Dependencies

### External APIs
- **OpenAI**: `gpt-3.5-turbo` for summarization, `dall-e-3` for images
- **WordPress REST API v2**: Posts and media endpoints with application password auth
- **News sources**: 180+ sites defined in `config/top_100_news_sites.txt`

### Content Safety Architecture
- **Input sanitization**: `markupsafe.escape()` for all user-provided content
- **AI content filtering**: Political/controversial topic detection and sanitization
- **Fallback content**: Default summaries/images when AI services fail

### Error Handling Conventions
- **Extensive logging**: All components log to console with timestamps
- **Graceful degradation**: Missing config files return empty defaults
- **Debug file generation**: JSON dumps for complex error scenarios
- **HTTP error passthrough**: OpenAI/WordPress API errors bubbled to frontend

## Testing Strategy

### Manual Testing Files
- `test_scraper.py`: Debug single news site with detailed output
- `test_openai.py`: Validate OpenAI API connectivity and model access
- `test_wordpress_upload.py`: Test media upload to WordPress
- `test_environment.py`: Comprehensive environment validation

### No Automated Test Suite
Current POC has limited automated testing. Use manual test scripts and Flask's built-in development server for debugging.

## Key Debugging Techniques

### Log Analysis
- Flask runs with debug logging enabled by default
- Check console output for detailed request/response information
- AI operations generate extensive debug artifacts in project root

### Configuration Validation
- Use `test_environment.py` to verify all dependencies
- WordPress API access testable via curl commands in setup docs
- OpenAI connectivity verified through multiple fallback methods

### Common Issues
- **Scraping failures**: Usually blocked by anti-bot measures, check user-agent rotation
- **AI errors**: Rate limiting or safety filters, check `debug_generate_image_error.json`
- **WordPress publishing**: Authentication issues, verify application password format
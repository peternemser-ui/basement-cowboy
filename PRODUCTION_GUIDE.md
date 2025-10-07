# Basement Cowboy - Production Ready

## 🚀 Quick Start

1. **Clone and Setup Environment:**
   ```bash
   git clone <repository>
   cd basement-cowboy
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configure Environment:**
   ```bash
   # Copy template and edit
   cp .env.template .env
   # Add your OpenAI API key to .env file
   ```

3. **Configure WordPress (optional):**
   ```bash
   cp config/wordpress_config.json.template config/wordpress_config.json
   # Edit with your WordPress credentials
   ```

4. **Run Application:**
   ```bash
   python run.py
   ```

## 📁 Project Structure

```
basement-cowboy/
├── app/                    # Main Flask application
│   ├── __init__.py
│   ├── routes.py          # Main routes and logic  
│   ├── seo_generator.py   # SEO optimization
│   ├── wordpress_graphql.py # WordPress GraphQL (optional)
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── config/                # Configuration files
│   ├── categories.json    # News categories
│   ├── top_100_news_sites.txt # News sources
│   └── wordpress_config.json.template
├── scraper/               # News scraping engine
│   ├── main.py           # Main scraper entry
│   ├── scrape_news.py    # News collection
│   ├── fetch_page.py     # Page fetching
│   ├── parse_articles.py # Content parsing
│   ├── filter_articles.py # Content filtering
│   ├── ai_enhancements.py # AI processing
│   └── dynamic_scraper.py # Dynamic content
├── output/               # Generated content
│   ├── news_articles/   # Scraped articles (JSON)
│   ├── logs/           # Application logs
│   └── wordpress-output/ # Published content
├── data/                # Application data
├── tests/              # Test suite
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies  
├── .env.template      # Environment variables template
└── README.md          # Documentation
```

## 🔧 Core Features

- **Automated News Scraping**: 180+ news sources
- **AI Enhancement**: OpenAI integration for summaries and images
- **Intelligent Ranking**: 7-factor quality scoring algorithm
- **WordPress Publishing**: Direct WordPress integration
- **SEO Optimization**: Automated meta tags and schema markup
- **Web Interface**: User-friendly article curation

## 🎯 Key Components

### News Scraping (`scraper/`)
- Scrapes 180+ news sites automatically
- Handles dynamic content with Playwright
- Filters and processes articles
- Saves to structured JSON files

### Flask Web App (`app/`)
- **routes.py**: Main application logic
- **seo_generator.py**: SEO optimization engine  
- **templates/**: Clean Bootstrap interface
- **static/**: CSS, JS, and assets

### Ranking Algorithm
- **Content Quality** (30%): Length, depth, readability
- **Source Credibility** (25%): Authority-based scoring
- **Title Engagement** (20%): SEO and engagement optimization
- **Visual Content** (10%): Image quality assessment
- **Timeliness** (10%): Urgency and relevance
- **Diversity** (10%): Category and geographic balance

## 📊 Usage Workflow

1. **Start Application**: `python run.py`
2. **Access Interface**: `http://localhost:5000`
3. **Enter OpenAI API Key**: Required for AI features
4. **Scrape News**: Click "Regenerate Articles" 
5. **Rank Articles**: Click "Rank Top 100"
6. **Review & Edit**: Customize summaries and images
7. **Publish**: Send to WordPress (optional)

## ⚙️ Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_openai_key_here
FLASK_SECRET_KEY=your_random_secret_key
ALLOW_UNSAFE_EVAL_FOR_DEV=0  # Keep 0 for production
```

### WordPress Integration (config/wordpress_config.json)
```json
{
  "wordpress_url": "https://your-site.com",
  "username": "your_wp_username", 
  "application_password": "xxxx xxxx xxxx xxxx"
}
```

## 🚦 Production Deployment

### Security Checklist
- ✅ Debug code removed
- ✅ Test files cleaned up
- ✅ Environment variables secured
- ✅ CSP headers properly configured
- ✅ Error handling improved
- ✅ Logging optimized for production

### Performance Optimizations
- ✅ Efficient ranking algorithm (0.03s)
- ✅ Bias elimination with randomization
- ✅ Optimized file handling
- ✅ Clean database-free architecture

## 📝 Recent Improvements

- **Enhanced Ranking Algorithm**: 7-factor sophisticated scoring
- **Bias Elimination**: True merit-based article selection
- **Code Cleanup**: Production-ready codebase
- **UI Fixes**: Proper article selection in interface
- **Performance**: Lightning-fast processing

## 🔧 Maintenance

- **Article Files**: Located in `output/news_articles/`
- **Logs**: Available in `output/logs/`
- **Configuration**: Edit files in `config/` directory
- **Updates**: Pull latest changes and restart application

---

**Status**: ✅ Production Ready
**Version**: Cleaned & Optimized
**Last Updated**: September 2025
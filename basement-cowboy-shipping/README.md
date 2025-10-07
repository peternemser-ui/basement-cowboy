# Basement Cowboy - AI News Aggregation Platform

![CI/CD Pipeline](https://github.com/peternemser-ui/basement-cowboy/workflows/CI/CD%20Pipeline%20-%20Basement%20Cowboy/badge.svg)
![Tests](https://github.com/peternemser-ui/basement-cowboy/workflows/Tests/badge.svg)
![Docker](https://github.com/peternemser-ui/basement-cowboy/workflows/Docker%20Build%20&%20Publish/badge.svg)

**Automated AI-powered news aggregation and publishing platform**  
**Status:** ✅ Production Ready with CI/CD  
**Version:** Production v1.0

---

## 🎯 What It Does

Basement Cowboy automatically:
1. **Scrapes 180+ news sources** for breaking articles
2. **Ranks articles** using advanced AI-powered 7-factor algorithm  
3. **Enhances content** with OpenAI summaries and generated images
4. **Publishes to WordPress** with SEO optimization
5. **Provides web interface** for human curation and oversight

## 🚀 Quick Start

### 🚀 Production Quick Start

**Windows:**
```batch
# One-click start (double-click in Windows Explorer)
start-cowboy.bat
```

**Linux/Mac:**
```bash
# Clone and setup
git clone <repository>
cd basement-cowboy
chmod +x start-production.sh
./start-production.sh
```

**Docker:**
```bash
# Quick Docker deployment
git clone <repository>
cd basement-cowboy
cp .env.template .env  # Edit with your API keys
docker-compose up -d
```

**Manual Setup:**
```bash
# 1. Environment setup
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
playwright install chromium

# 2. Configuration
cp .env.template .env
# Edit .env with your OpenAI API key

# 3. Start application
python run.py
# Access: http://localhost:5000
```

## ✨ Key Features

### 🤖 Intelligent AI Processing
- **Smart Article Ranking**: 7-factor quality algorithm (content, credibility, engagement)
- **OpenAI Integration**: GPT-3.5 summaries + DALL-E 3 image generation
- **Bias Elimination**: Merit-based selection across all sources

### 📰 Comprehensive News Coverage  
- **180+ News Sources**: Reuters, AP, BBC, CNN, and many more
- **Dynamic Scraping**: Handles JavaScript-heavy sites with Playwright
- **Content Filtering**: Removes duplicates and low-quality articles

### 🎨 Modern Web Interface
- **Bootstrap 5.3 UI**: Clean, responsive design
- **Real-time Updates**: Live scraping progress and article ranking
- **One-click Actions**: Rank top 100, generate summaries, create images

### 📊 WordPress Integration
- **Direct Publishing**: REST API integration with media uploads
- **SEO Optimization**: Automated meta tags, schema markup
- **Structured Data**: JSON embedding for theme consumption

### 🔒 Production Security
- **Session-based API Keys**: Secure OpenAI key management
- **Environment Variables**: Sensitive data protection
- **Error Handling**: Graceful degradation and logging

## 🏗️ Architecture

```
News Sources → Scraper → JSON Storage → Flask UI → AI Enhancement → WordPress
```

**File-based Architecture**: No database required - articles stored as JSON files  
**Session Management**: Secure API key handling with Flask sessions  
**Modular Design**: Separate components for scraping, ranking, and publishing

## 📋 Requirements

- **Python 3.11+** 
- **8GB RAM minimum** (16GB recommended)
- **5GB storage** for articles and logs
- **OpenAI API Key** (GPT-3.5/4 + DALL-E 3 access)
- **WordPress site** (optional, for publishing)

## 🔧 Configuration

### Essential Setup (.env file)
```bash
OPENAI_API_KEY=sk-proj-your-key-here
FLASK_SECRET_KEY=your-random-secret-key-here
```

### Optional WordPress (config/wordpress_config.json)
```json
{
  "wordpress_url": "https://your-site.com",
  "username": "your-username",
  "application_password": "xxxx xxxx xxxx xxxx"
}
```

## � Usage Guide

1. **Launch**: `python run.py` → Open `http://localhost:5000`
2. **API Key**: Enter OpenAI API key (stored in session, not saved)
3. **Scrape**: Click "Regenerate Articles" to collect news
4. **Rank**: Click "Rank Top 100" to select best articles  
5. **Enhance**: Add AI summaries and images to selected articles
6. **Publish**: Send to WordPress or export data

## 🎯 Ranking Algorithm

**7-Factor Intelligent Scoring:**
- **Content Quality** (30%): Article depth, length, readability
- **Source Credibility** (25%): Authority database of 100+ sources
- **Title Engagement** (20%): SEO optimization, clickbait detection  
- **Visual Content** (10%): Image presence and quality
- **Timeliness** (10%): Urgency keywords, breaking news indicators
- **Category Diversity** (5%): Balanced topic coverage
- **Geographic Diversity** (5%): Global news representation

**Result**: Lightning-fast (0.03s) merit-based article selection with zero positional bias.

## 🗂️ Project Structure

## ⚙️ Enhanced Configuration

### Enhanced Environment Variables (.env)
```env
# Flask Configuration
FLASK_SECRET_KEY=your-random-32-character-secret-key
```
basement-cowboy/
├── app/                    # Flask application
│   ├── routes.py          # Main logic & API endpoints
│   ├── seo_generator.py   # SEO optimization
│   ├── templates/         # HTML templates  
│   └── static/           # CSS, JS, images
├── scraper/               # News scraping engine
│   ├── scrape_news.py    # Main scraper
│   └── *.py              # Supporting modules
├── config/               # Configuration files
├── output/               # Generated articles & logs
├── run.py                # Application entry point
└── requirements.txt      # Dependencies
```

## 🚀 Production Ready

This codebase has been thoroughly cleaned and optimized for production:

- ✅ **Debug code removed** - No development artifacts
- ✅ **Security hardened** - Secure API key handling  
- ✅ **Performance optimized** - Lightning-fast ranking (0.03s)
- ✅ **Error handling** - Graceful degradation
- ✅ **Code quality** - Clean, documented, maintainable
- ✅ **Bias eliminated** - Fair article selection algorithm

## 📚 Documentation

- **[PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)** - Detailed deployment guide
- **[TECHNICAL_BRIEF.md](TECHNICAL_BRIEF.md)** - Technical architecture
- **[WP_ENGINE_QUICK_SETUP.md](WP_ENGINE_QUICK_SETUP.md)** - WordPress setup

---

**Ready to ship!** 🚢  
*Clean, fast, and production-ready AI news aggregation platform.*
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

## 🎯 Enhanced Usage Workflow

### 1. **Start Enhanced Application**
```bash
python run.py
```
Access enhanced interface at: http://127.0.0.1:5000

### 2. **Secure API Key Management**
- **Enhanced Security**: Beautiful web interface for secure API key entry
- **Real-time Validation**: Live validation with OpenAI API capabilities check
- **Session Storage**: API keys stored securely in browser sessions only
- **Advanced Features**: Model access verification and capability detection

### 3. **Enhanced News Scraping**
- **Real-time Progress**: Live scraping updates with auto-refresh
- **AI-Powered Ranking**: Intelligent article quality scoring
- **Performance Monitoring**: Success rates and timing metrics
- **Enhanced Filtering**: Advanced content quality assessment

### 4. **Advanced Article Selection**
- **Smart Grid View**: Enhanced visual layout with image previews
- **Dynamic Goals**: 100 minimum, 150 target article selection
- **Quality Indicators**: Visual cues for article quality and completeness
- **Progress Tracking**: Real-time counter with color-coded feedback

### 5. **AI Enhancement with SEO**
- **GPT-4 Summaries**: Advanced content summarization
- **SEO Metadata**: Comprehensive schema markup and meta tag generation
- **DALL-E 3 Images**: Strategic image generation with safety filtering
- **Content Optimization**: Readability scoring and improvement suggestions

### 6. **Strategic WordPress Publishing**
- **Enhanced Pipeline**: Bulk publishing with real-time progress
- **Template Integration**: Custom WordPress templates with image algorithms
- **SEO Integration**: Structured data embedding for search optimization
- **Media Management**: Automatic WordPress media library integration

## 🔬 Enhanced Testing

Comprehensive test suite in the `tests/` directory:

- `test_seo.py` - SEO generator functionality validation
- `test_ui_guide.py` - Enhanced UI component testing  
- `test_comprehensive.py` - Full system integration testing
- `test_ranking.py` - Article ranking algorithm validation
- `test_wordpress_connection.py` - Advanced WordPress API testing

## 🛠️ Enhanced Development

### Advanced Debug Mode
Set `FLASK_DEBUG=True` in `.env` for enhanced development features:
- **Auto-reload**: Instant updates on file changes
- **Enhanced Error Pages**: Detailed debugging information
- **Performance Monitoring**: Request timing and resource usage
- **SEO Debug Mode**: Detailed metadata generation logging

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

## 🆘 Enhanced Troubleshooting

### Enhanced Issues Coverage

**SEO Generator Problems**
- Test SEO functionality: `python tests/test_seo.py`
- Verify schema markup generation and meta tag creation
- Check WordPress SEO plugin compatibility

**WordPress Template Issues**
- Verify custom template deployment: `ls /wp-content/themes/your-theme/wordpress-template-with-images.php`
- Check template permissions and WordPress template selection
- Validate image placement algorithms and responsive layout

**Enhanced UI Problems**
- Check static file serving: verify `app/static/styles.css` exists
- Verify Bootstrap and Font Awesome CDN loading
- Test JavaScript functionality and session management

**API Key Session Management**
- Clear browser cookies and retry API key entry
- Test session functionality with Flask secret key validation
- Verify OpenAI API connectivity and model access

**Enhanced Scraping Failures**
- Test enhanced scraper components: `python tests/test_comprehensive.py`
- Check Playwright browser installation: `playwright install chromium`
- Verify AI ranking system and content filtering

### Advanced Support Resources

1. **Enhanced Setup Guide**: `Basement-Cowboy-Enhanced-Setup-Guide.md`
2. **Comprehensive Test Suite**: Run `python -m pytest tests/` for validation
3. **Component Testing**: Individual feature testing scripts available
4. **Performance Monitoring**: Built-in metrics and logging systems

---

## 📊 Enhanced Performance Metrics

### System Capabilities (v2.0)
- **Scraping Performance**: 180+ sources in 15-30 minutes with AI ranking
- **AI Processing**: 100 articles with summaries + SEO in 12-18 minutes
- **SEO Generation**: Complete metadata for 150 articles in 2-3 minutes
- **Publishing Speed**: Bulk WordPress publishing 50+ articles in 5-10 minutes
- **Template Performance**: Sub-second rendering with strategic image caching

### Resource Requirements (Enhanced)
- **Memory Usage**: 8-16GB during peak AI and SEO processing
- **Storage Growth**: 15-25MB per enhanced scraping session
- **Network Bandwidth**: 750MB-1.5GB per complete cycle with images
- **API Costs**: $15-35 per day with full AI enhancement and SEO features

---

## 🔒 Enhanced Security Features

- **Session-based API Management**: Secure OpenAI key storage in browser sessions only
- **Advanced Content Filtering**: AI-powered inappropriate content detection
- **WordPress Security**: Application password authentication with session persistence
- **Input Sanitization**: Comprehensive XSS and injection protection
- **SEO Security**: Schema markup validation and meta tag sanitization

---

## 🚀 Next Steps (v2.0)

This enhanced system is ready for:
1. **Production Deployment** with comprehensive SEO optimization
2. **Performance Analytics** tracking with enhanced metrics
3. **Content Quality Analysis** using AI-powered assessment
4. **SEO Performance Monitoring** with search ranking validation
5. **Advanced UI Enhancement** planning for Phase 3

---

**Enhanced Status:** ✅ **Production Ready with Advanced SEO & UI Features**

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

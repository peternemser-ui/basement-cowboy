# 🚀 Basement Cowboy - Production Deployment Guide

## 📋 Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browser installed (`playwright install chromium`)
- [ ] Environment variables configured (`.env` file)
- [ ] WordPress configuration set up (if using publishing features)

### ✅ Security Checklist
- [ ] `.env` file contains placeholder values (no real API keys committed)
- [ ] WordPress credentials in `config/wordpress_config.json` are secure
- [ ] Flask debug mode disabled in production
- [ ] All debug code and files removed
- [ ] Secret keys are randomly generated and secure

---

## 🔧 Quick Start Instructions

### 1. Clone and Environment Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd basement-cowboy

# Windows One-Click Start
start-cowboy.bat

# OR Manual Setup:
# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create virtual environment (Linux/Mac)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

### 2. Environment Configuration
```bash
# Copy and edit environment file
cp .env.template .env
# Edit .env with your actual values:
# - Add your OpenAI API key
# - Set FLASK_DEBUG=False for production
# - Generate secure FLASK_SECRET_KEY
```

### 3. WordPress Configuration (Optional)
```bash
# Copy and edit WordPress config
cp config/wordpress_config.json.template config/wordpress_config.json
# Edit with your WordPress credentials
```

### 4. Run the Application
```bash
# Start the application
python run.py

# Access the web interface
# Open browser to: http://localhost:5000
```

---

## 🏗️ Production Deployment

### Environment Variables (`.env`)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your-actual-openai-api-key

# Flask Configuration  
FLASK_SECRET_KEY=your-32-character-random-secret-key
FLASK_DEBUG=False

# Optional: DALL-E Configuration
DALL_E_MODEL=dall-e-3
IMAGE_SIZE=1024x1024
```

### WordPress Configuration (`config/wordpress_config.json`)
```json
{
    "wordpress_url": "https://yoursite.com",
    "username": "your-wp-username", 
    "application_password": "xxxx xxxx xxxx xxxx"
}
```

### Production Server Setup

#### Option 1: Direct Python Deployment
```bash
# Production start
python run.py
```

#### Option 2: Gunicorn (Recommended)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### Option 3: Docker Deployment
```bash
# Build Docker image
docker build -t basement-cowboy .

# Run container
docker run -p 5000:5000 --env-file .env basement-cowboy
```

---

## 📊 System Architecture

### Core Components
1. **News Scraper** (`scraper/`) - Automated news collection from 180+ sources
2. **Flask Web App** (`app/`) - Web interface and API endpoints
3. **AI Enhancement** - OpenAI integration for summaries and images
4. **WordPress Publishing** - Direct WordPress REST API integration
5. **SEO Generator** - Automated SEO optimization

### Data Flow
```
News Sources → Scraper → JSON Storage → Web UI → AI Enhancement → WordPress
```

### File Structure
```
basement-cowboy/
├── app/                    # Flask application
├── scraper/               # News scraping engine  
├── config/                # Configuration files
├── output/                # Generated content
│   ├── news_articles/    # Scraped articles (JSON)
│   └── wordpress-output/ # Published content
├── tests/                 # Test suite
├── run.py                # Application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

---

## 🔍 Operation & Monitoring

### Daily Operations
1. **Start Application**: `python run.py`
2. **Monitor Logs**: Check console output for errors
3. **Review Articles**: Use web interface at `http://localhost:5000`
4. **Publish Content**: Use "Publish to WordPress" feature

### Health Checks
- **Application Status**: Check if `http://localhost:5000` is accessible
- **Scraper Status**: Monitor scraping success rates in logs
- **AI Services**: Verify OpenAI API connectivity
- **WordPress**: Test publishing functionality

### Troubleshooting
- **Scraping Issues**: Check user-agent rotation and site blocking
- **AI Errors**: Verify OpenAI API key and rate limits
- **WordPress Problems**: Check authentication and API access
- **Performance**: Monitor memory usage during large scraping operations

---

## 🛡️ Security Considerations

### API Key Management
- Never commit real API keys to version control
- Use environment variables for all sensitive data
- Rotate API keys regularly
- Monitor API usage for anomalies

### Application Security
- Run with `FLASK_DEBUG=False` in production
- Use secure secret keys (32+ random characters)
- Keep dependencies updated
- Monitor for security vulnerabilities

### Data Privacy
- Review scraped content for compliance
- Respect robots.txt files
- Implement rate limiting for scraping
- Consider GDPR/privacy implications

---

## 📈 Performance Optimization

### Scraping Performance
- Adjust concurrent request limits
- Implement intelligent retry logic
- Use caching for repeated requests
- Monitor target site response times

### Application Performance
- Use Gunicorn for production serving
- Implement database caching if needed
- Optimize image processing
- Monitor memory usage

---

## 🔧 Maintenance

### Regular Tasks
- **Update Dependencies**: `pip install -r requirements.txt --upgrade`
- **Clean Output Files**: Remove old JSON files periodically
- **Update News Sources**: Review and update source list
- **Monitor API Usage**: Track OpenAI API consumption

### Backup Strategy
- **Configuration Files**: Backup `config/` directory
- **Generated Content**: Backup `output/` directory
- **Database**: If using database, implement regular backups
- **Environment Files**: Secure backup of production `.env`

---

## 📞 Support & Documentation

### Additional Resources
- `README.md` - Project overview and features
- `TECHNICAL_BRIEF.md` - Technical architecture details
- `WP_ENGINE_QUICK_SETUP.md` - WordPress-specific setup
- `tests/` - Test suite for validation

### Getting Help
1. Check logs for specific error messages
2. Review configuration files for missing values
3. Test individual components using test files
4. Consult OpenAI/WordPress API documentation
5. Check GitHub issues for known problems

---

**🎯 Ready for Production!**

This application is now clean, secure, and ready for production deployment. Follow the checklist above to ensure a smooth deployment process.
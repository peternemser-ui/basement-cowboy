"""Application constants."""

# Application info
APP_NAME = "Basement Cowboy"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered news aggregation and publishing platform"

# Default categories
DEFAULT_CATEGORIES = [
    "World",
    "Politics",
    "Business",
    "Technology",
    "Science",
    "Health",
    "Entertainment",
    "Sports",
    "Opinion",
    "Lifestyle",
    "Environment",
    "Education",
    "Crime",
    "Culture",
    "Travel",
]

# Reliable news sources with credibility scores
CREDIBLE_SOURCES = {
    'reuters.com': 0.95,
    'apnews.com': 0.95,
    'bbc.com': 0.90,
    'bbc.co.uk': 0.90,
    'npr.org': 0.88,
    'pbs.org': 0.88,
    'nytimes.com': 0.85,
    'washingtonpost.com': 0.85,
    'theguardian.com': 0.85,
    'wsj.com': 0.85,
    'economist.com': 0.85,
    'ft.com': 0.85,
    'bloomberg.com': 0.82,
    'cnn.com': 0.75,
    'cbsnews.com': 0.75,
    'nbcnews.com': 0.75,
    'abcnews.go.com': 0.75,
    'usatoday.com': 0.70,
    'foxnews.com': 0.70,
    'msnbc.com': 0.70,
}

# HTTP request settings
DEFAULT_TIMEOUT = 30
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Rate limiting
DEFAULT_REQUEST_DELAY = 1.0
MAX_REQUESTS_PER_MINUTE = 30
MAX_CONCURRENT_REQUESTS = 5

# Article limits
MAX_ARTICLES_PER_SOURCE = 10
MAX_TOTAL_ARTICLES = 500
MIN_CONTENT_LENGTH = 100
MAX_CONTENT_LENGTH = 50000

# SEO settings
MAX_TITLE_LENGTH = 60
MAX_DESCRIPTION_LENGTH = 160
MAX_KEYWORDS = 10

# OpenAI settings
DEFAULT_CHAT_MODEL = "gpt-3.5-turbo"
DEFAULT_IMAGE_MODEL = "dall-e-3"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

# Cost limits
DEFAULT_MAX_COST_PER_ARTICLE = 0.50
DEFAULT_MAX_DAILY_COST = 50.00
DEFAULT_MAX_MONTHLY_COST = 500.00

# WordPress settings
DEFAULT_POST_STATUS = "draft"
DEFAULT_IMAGE_QUALITY = 85
MAX_IMAGE_WIDTH = 1200

# Cache settings
MEMORY_CACHE_SIZE = 1000
MEMORY_CACHE_TTL = 300  # 5 minutes
FILE_CACHE_TTL = 3600  # 1 hour

# Logging
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# File paths
DEFAULT_DATA_DIR = "data"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOGS_DIR = "output/logs"
DEFAULT_CACHE_DIR = "output/cache"
DEFAULT_ARTICLES_DIR = "output/news_articles"

# Supported file types
SUPPORTED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp']
SUPPORTED_EXPORT_FORMATS = ['json', 'jsonl', 'csv']

# Status codes
class StatusCodes:
    """HTTP-like status codes for internal use."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    RATE_LIMITED = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503

# Error codes
class ErrorCodes:
    """Application error codes."""
    UNKNOWN = "UNKNOWN_ERROR"
    VALIDATION = "VALIDATION_ERROR"
    CONFIGURATION = "CONFIGURATION_ERROR"
    AUTHENTICATION = "AUTHENTICATION_ERROR"
    RATE_LIMIT = "RATE_LIMIT_ERROR"
    API_ERROR = "API_ERROR"
    SCRAPER_ERROR = "SCRAPER_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    WORDPRESS_ERROR = "WORDPRESS_ERROR"
    OPENAI_ERROR = "OPENAI_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DUPLICATE = "DUPLICATE_ERROR"
    COST_LIMIT = "COST_LIMIT_ERROR"

# Ranking weights presets
RANKING_PRESETS = {
    'default': {
        'quality': 0.20,
        'credibility': 0.20,
        'engagement': 0.15,
        'visuals': 0.10,
        'timeliness': 0.15,
        'category_diversity': 0.10,
        'geographic_diversity': 0.10,
    },
    'quality_focused': {
        'quality': 0.30,
        'credibility': 0.30,
        'engagement': 0.10,
        'visuals': 0.05,
        'timeliness': 0.10,
        'category_diversity': 0.08,
        'geographic_diversity': 0.07,
    },
    'engagement_focused': {
        'quality': 0.15,
        'credibility': 0.15,
        'engagement': 0.25,
        'visuals': 0.20,
        'timeliness': 0.10,
        'category_diversity': 0.08,
        'geographic_diversity': 0.07,
    },
    'breaking_news': {
        'quality': 0.15,
        'credibility': 0.20,
        'engagement': 0.10,
        'visuals': 0.10,
        'timeliness': 0.30,
        'category_diversity': 0.08,
        'geographic_diversity': 0.07,
    },
}

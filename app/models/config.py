"""Configuration data models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import os


@dataclass
class ScraperConfig:
    """Configuration for the news scraper."""
    # Sources
    sources_file: str = "config/top_100_news_sites.txt"
    categories_file: str = "config/categories.json"

    # Timing
    request_delay: float = 1.0
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0

    # Limits
    max_articles_per_source: int = 10
    max_total_articles: int = 500
    min_content_length: int = 100

    # Browser
    use_playwright: bool = True
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    # Filtering
    exclude_domains: List[str] = field(default_factory=list)
    required_keywords: List[str] = field(default_factory=list)
    blocked_keywords: List[str] = field(default_factory=list)

    # Output
    output_dir: str = "output/news_articles"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sources_file': self.sources_file,
            'categories_file': self.categories_file,
            'request_delay': self.request_delay,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'max_articles_per_source': self.max_articles_per_source,
            'max_total_articles': self.max_total_articles,
            'min_content_length': self.min_content_length,
            'use_playwright': self.use_playwright,
            'headless': self.headless,
            'user_agent': self.user_agent,
            'exclude_domains': self.exclude_domains,
            'required_keywords': self.required_keywords,
            'blocked_keywords': self.blocked_keywords,
            'output_dir': self.output_dir,
        }

    @classmethod
    def from_env(cls) -> 'ScraperConfig':
        """Load configuration from environment variables."""
        return cls(
            request_delay=float(os.getenv('SCRAPER_DELAY', '1.0')),
            timeout=int(os.getenv('SCRAPER_TIMEOUT', '30')),
            max_retries=int(os.getenv('SCRAPER_MAX_RETRIES', '3')),
            max_articles_per_source=int(os.getenv('SCRAPER_MAX_PER_SOURCE', '10')),
            max_total_articles=int(os.getenv('SCRAPER_MAX_TOTAL', '500')),
            use_playwright=os.getenv('SCRAPER_USE_PLAYWRIGHT', 'true').lower() == 'true',
            headless=os.getenv('SCRAPER_HEADLESS', 'true').lower() == 'true',
            output_dir=os.getenv('SCRAPER_OUTPUT_DIR', 'output/news_articles'),
        )


@dataclass
class WordPressConfig:
    """Configuration for WordPress integration."""
    site_url: str = ""
    username: str = ""
    password: str = ""

    # API settings
    use_graphql: bool = True
    graphql_endpoint: str = "/graphql"
    rest_endpoint: str = "/wp-json/wp/v2"

    # Publishing defaults
    default_status: str = "draft"
    default_author: Optional[int] = None
    default_category: Optional[int] = None

    # Media settings
    upload_images: bool = True
    image_quality: int = 85
    max_image_width: int = 1200

    # SEO
    enable_yoast: bool = True
    enable_schema: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'site_url': self.site_url,
            'username': self.username,
            'use_graphql': self.use_graphql,
            'graphql_endpoint': self.graphql_endpoint,
            'rest_endpoint': self.rest_endpoint,
            'default_status': self.default_status,
            'default_author': self.default_author,
            'default_category': self.default_category,
            'upload_images': self.upload_images,
            'image_quality': self.image_quality,
            'max_image_width': self.max_image_width,
            'enable_yoast': self.enable_yoast,
            'enable_schema': self.enable_schema,
        }

    @classmethod
    def from_env(cls) -> 'WordPressConfig':
        """Load configuration from environment variables."""
        return cls(
            site_url=os.getenv('WORDPRESS_URL', ''),
            username=os.getenv('WORDPRESS_USERNAME', ''),
            password=os.getenv('WORDPRESS_PASSWORD', ''),
            use_graphql=os.getenv('WORDPRESS_USE_GRAPHQL', 'true').lower() == 'true',
            default_status=os.getenv('WORDPRESS_DEFAULT_STATUS', 'draft'),
            upload_images=os.getenv('WORDPRESS_UPLOAD_IMAGES', 'true').lower() == 'true',
        )

    def is_configured(self) -> bool:
        """Check if WordPress is properly configured."""
        return bool(self.site_url and self.username and self.password)


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI integration."""
    api_key: str = ""

    # Model settings
    chat_model: str = "gpt-3.5-turbo"
    image_model: str = "dall-e-3"

    # Generation settings
    max_tokens: int = 500
    temperature: float = 0.7

    # Image settings
    image_size: str = "1024x1024"
    image_quality: str = "standard"

    # Cost tracking
    track_costs: bool = True
    max_cost_per_article: float = 0.50
    max_daily_cost: float = 50.00

    def to_dict(self) -> Dict[str, Any]:
        return {
            'chat_model': self.chat_model,
            'image_model': self.image_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'image_size': self.image_size,
            'image_quality': self.image_quality,
            'track_costs': self.track_costs,
            'max_cost_per_article': self.max_cost_per_article,
            'max_daily_cost': self.max_daily_cost,
        }

    @classmethod
    def from_env(cls) -> 'OpenAIConfig':
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv('OPENAI_API_KEY', ''),
            chat_model=os.getenv('OPENAI_CHAT_MODEL', 'gpt-3.5-turbo'),
            image_model=os.getenv('OPENAI_IMAGE_MODEL', 'dall-e-3'),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '500')),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
            max_cost_per_article=float(os.getenv('OPENAI_MAX_COST_PER_ARTICLE', '0.50')),
            max_daily_cost=float(os.getenv('OPENAI_MAX_DAILY_COST', '50.00')),
        )

    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return bool(self.api_key)


@dataclass
class AppConfig:
    """Main application configuration."""
    # Flask settings
    debug: bool = False
    secret_key: str = ""
    host: str = "0.0.0.0"
    port: int = 5000

    # Sub-configurations
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    wordpress: WordPressConfig = field(default_factory=WordPressConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)

    # Paths
    data_dir: str = "data"
    output_dir: str = "output"
    logs_dir: str = "output/logs"

    # Features
    enable_ai_enhancement: bool = True
    enable_image_generation: bool = True
    enable_seo: bool = True

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load full configuration from environment."""
        return cls(
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key'),
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', '5000')),
            scraper=ScraperConfig.from_env(),
            wordpress=WordPressConfig.from_env(),
            openai=OpenAIConfig.from_env(),
            data_dir=os.getenv('DATA_DIR', 'data'),
            output_dir=os.getenv('OUTPUT_DIR', 'output'),
            logs_dir=os.getenv('LOGS_DIR', 'output/logs'),
            enable_ai_enhancement=os.getenv('ENABLE_AI', 'true').lower() == 'true',
            enable_image_generation=os.getenv('ENABLE_IMAGES', 'true').lower() == 'true',
            enable_seo=os.getenv('ENABLE_SEO', 'true').lower() == 'true',
        )

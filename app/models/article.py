"""Article data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class ArticleStatus(Enum):
    """Status of an article in the pipeline."""
    SCRAPED = "scraped"
    RANKED = "ranked"
    ENHANCED = "enhanced"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ERROR = "error"


@dataclass
class ArticleSource:
    """Source information for an article."""
    name: str
    url: str
    domain: str
    reliability_score: float = 0.5
    category: Optional[str] = None
    country: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'url': self.url,
            'domain': self.domain,
            'reliability_score': self.reliability_score,
            'category': self.category,
            'country': self.country,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArticleSource':
        return cls(
            name=data.get('name', ''),
            url=data.get('url', ''),
            domain=data.get('domain', ''),
            reliability_score=data.get('reliability_score', 0.5),
            category=data.get('category'),
            country=data.get('country'),
        )


@dataclass
class Article:
    """Represents a news article."""
    id: str
    title: str
    url: str
    source: ArticleSource
    scraped_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    status: ArticleStatus = ArticleStatus.SCRAPED

    # Content fields
    content: str = ""
    summary: str = ""
    excerpt: str = ""

    # Media
    image_url: Optional[str] = None
    generated_image_url: Optional[str] = None
    images: List[str] = field(default_factory=list)

    # Metadata
    author: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Ranking
    rank_score: float = 0.0
    ranking_details: Dict[str, float] = field(default_factory=dict)

    # Processing
    ai_summary: Optional[str] = None
    ai_cost: float = 0.0
    wordpress_id: Optional[int] = None
    wordpress_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'source': self.source.to_dict() if isinstance(self.source, ArticleSource) else self.source,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'status': self.status.value if isinstance(self.status, ArticleStatus) else self.status,
            'content': self.content,
            'summary': self.summary,
            'excerpt': self.excerpt,
            'image_url': self.image_url,
            'generated_image_url': self.generated_image_url,
            'images': self.images,
            'author': self.author,
            'category': self.category,
            'tags': self.tags,
            'rank_score': self.rank_score,
            'ranking_details': self.ranking_details,
            'ai_summary': self.ai_summary,
            'ai_cost': self.ai_cost,
            'wordpress_id': self.wordpress_id,
            'wordpress_url': self.wordpress_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create article from dictionary."""
        source_data = data.get('source', {})
        if isinstance(source_data, dict):
            source = ArticleSource.from_dict(source_data)
        else:
            source = ArticleSource(name='', url='', domain='')

        scraped_at = data.get('scraped_at')
        if isinstance(scraped_at, str):
            scraped_at = datetime.fromisoformat(scraped_at)
        elif not isinstance(scraped_at, datetime):
            scraped_at = datetime.now()

        published_at = data.get('published_at')
        if isinstance(published_at, str):
            published_at = datetime.fromisoformat(published_at)

        status = data.get('status', 'scraped')
        if isinstance(status, str):
            try:
                status = ArticleStatus(status)
            except ValueError:
                status = ArticleStatus.SCRAPED

        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            url=data.get('url', ''),
            source=source,
            scraped_at=scraped_at,
            published_at=published_at,
            status=status,
            content=data.get('content', ''),
            summary=data.get('summary', ''),
            excerpt=data.get('excerpt', ''),
            image_url=data.get('image_url'),
            generated_image_url=data.get('generated_image_url'),
            images=data.get('images', []),
            author=data.get('author'),
            category=data.get('category'),
            tags=data.get('tags', []),
            rank_score=data.get('rank_score', 0.0),
            ranking_details=data.get('ranking_details', {}),
            ai_summary=data.get('ai_summary'),
            ai_cost=data.get('ai_cost', 0.0),
            wordpress_id=data.get('wordpress_id'),
            wordpress_url=data.get('wordpress_url'),
        )

    def is_valid(self) -> bool:
        """Check if article has minimum required fields."""
        return bool(self.title and self.url)

    def has_content(self) -> bool:
        """Check if article has substantive content."""
        return len(self.content) > 100

    def has_image(self) -> bool:
        """Check if article has any image."""
        return bool(self.image_url or self.generated_image_url or self.images)

"""API request/response models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


@dataclass
class APIError:
    """API error response."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details,
                'timestamp': self.timestamp.isoformat(),
            }
        }

    @classmethod
    def validation_error(cls, message: str, field: Optional[str] = None) -> 'APIError':
        """Create a validation error."""
        details = {'field': field} if field else None
        return cls(code='VALIDATION_ERROR', message=message, details=details)

    @classmethod
    def not_found(cls, resource: str, id: Any) -> 'APIError':
        """Create a not found error."""
        return cls(
            code='NOT_FOUND',
            message=f"{resource} not found",
            details={'resource': resource, 'id': str(id)}
        )

    @classmethod
    def internal_error(cls, message: str = "Internal server error") -> 'APIError':
        """Create an internal server error."""
        return cls(code='INTERNAL_ERROR', message=message)

    @classmethod
    def rate_limited(cls, retry_after: int = 60) -> 'APIError':
        """Create a rate limit error."""
        return cls(
            code='RATE_LIMITED',
            message="Too many requests",
            details={'retry_after': retry_after}
        )

    @classmethod
    def unauthorized(cls, message: str = "Authentication required") -> 'APIError':
        """Create an unauthorized error."""
        return cls(code='UNAUTHORIZED', message=message)


@dataclass
class APIResponse:
    """Generic API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[APIError] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {'success': self.success}

        if self.data is not None:
            result['data'] = self.data

        if self.error:
            result['error'] = self.error.to_dict()['error']

        if self.meta:
            result['meta'] = self.meta

        return result

    @classmethod
    def ok(cls, data: Any = None, meta: Optional[Dict] = None) -> 'APIResponse':
        """Create a success response."""
        return cls(success=True, data=data, meta=meta or {})

    @classmethod
    def fail(cls, error: APIError) -> 'APIResponse':
        """Create a failure response."""
        return cls(success=False, error=error)


@dataclass
class PaginatedResponse:
    """Paginated API response."""
    items: List[Any]
    total: int
    page: int = 1
    per_page: int = 20

    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            'items': self.items,
            'pagination': {
                'total': self.total,
                'page': self.page,
                'per_page': self.per_page,
                'total_pages': self.total_pages,
                'has_next': self.has_next,
                'has_prev': self.has_prev,
            }
        }


@dataclass
class ScrapeRequest:
    """Request to scrape articles."""
    sources: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    max_articles: int = 100
    include_content: bool = True
    use_playwright: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sources': self.sources,
            'categories': self.categories,
            'max_articles': self.max_articles,
            'include_content': self.include_content,
            'use_playwright': self.use_playwright,
        }


@dataclass
class RankRequest:
    """Request to rank articles."""
    article_ids: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None
    top_n: int = 10
    category_filter: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'article_ids': self.article_ids,
            'weights': self.weights,
            'top_n': self.top_n,
            'category_filter': self.category_filter,
        }


@dataclass
class EnhanceRequest:
    """Request to enhance an article with AI."""
    article_id: str
    generate_summary: bool = True
    generate_image: bool = False
    image_prompt: Optional[str] = None
    summary_style: str = "concise"  # concise, detailed, bullet_points

    def to_dict(self) -> Dict[str, Any]:
        return {
            'article_id': self.article_id,
            'generate_summary': self.generate_summary,
            'generate_image': self.generate_image,
            'image_prompt': self.image_prompt,
            'summary_style': self.summary_style,
        }


@dataclass
class PublishRequest:
    """Request to publish an article."""
    article_id: str
    status: str = "draft"
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    schedule_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'article_id': self.article_id,
            'status': self.status,
            'category_id': self.category_id,
            'tag_ids': self.tag_ids,
            'schedule_date': self.schedule_date.isoformat() if self.schedule_date else None,
        }

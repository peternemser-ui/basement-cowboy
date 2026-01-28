"""Custom exception classes."""

from typing import Optional, Dict, Any


class BasementCowboyError(Exception):
    """Base exception for all Basement Cowboy errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'error': {
                'code': self.code,
                'message': self.message,
                'details': self.details,
            }
        }


class ConfigurationError(BasementCowboyError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details={'config_key': config_key} if config_key else {},
        )


class ValidationError(BasementCowboyError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)[:100]  # Truncate long values

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details,
        )


class APIError(BasementCowboyError):
    """Raised when an external API call fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        response_body: Optional[str] = None,
    ):
        details = {}
        if status_code:
            details['status_code'] = status_code
        if api_name:
            details['api'] = api_name
        if response_body:
            details['response'] = response_body[:500]  # Truncate

        super().__init__(
            message=message,
            code="API_ERROR",
            details=details,
        )


class ScraperError(BasementCowboyError):
    """Raised when scraping fails."""

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        source: Optional[str] = None,
    ):
        details = {}
        if url:
            details['url'] = url
        if source:
            details['source'] = source

        super().__init__(
            message=message,
            code="SCRAPER_ERROR",
            details=details,
        )


class RateLimitError(BasementCowboyError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        limit_type: Optional[str] = None,
    ):
        details = {}
        if retry_after:
            details['retry_after'] = retry_after
        if limit_type:
            details['limit_type'] = limit_type

        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            details=details,
        )


class AuthenticationError(BasementCowboyError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required", service: Optional[str] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details={'service': service} if service else {},
        )


class WordPressError(BasementCowboyError):
    """Raised when WordPress operations fail."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        post_id: Optional[int] = None,
    ):
        details = {}
        if operation:
            details['operation'] = operation
        if post_id:
            details['post_id'] = post_id

        super().__init__(
            message=message,
            code="WORDPRESS_ERROR",
            details=details,
        )


class OpenAIError(BasementCowboyError):
    """Raised when OpenAI API operations fail."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        details = {}
        if model:
            details['model'] = model
        if operation:
            details['operation'] = operation

        super().__init__(
            message=message,
            code="OPENAI_ERROR",
            details=details,
        )


class StorageError(BasementCowboyError):
    """Raised when storage operations fail."""

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
    ):
        details = {}
        if path:
            details['path'] = path
        if operation:
            details['operation'] = operation

        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            details=details,
        )


class ArticleNotFoundError(BasementCowboyError):
    """Raised when an article is not found."""

    def __init__(self, article_id: str):
        super().__init__(
            message=f"Article not found: {article_id}",
            code="ARTICLE_NOT_FOUND",
            details={'article_id': article_id},
        )


class DuplicateArticleError(BasementCowboyError):
    """Raised when attempting to create a duplicate article."""

    def __init__(self, url: str, existing_id: Optional[str] = None):
        details = {'url': url}
        if existing_id:
            details['existing_id'] = existing_id

        super().__init__(
            message=f"Article already exists: {url}",
            code="DUPLICATE_ARTICLE",
            details=details,
        )


class CostLimitError(BasementCowboyError):
    """Raised when cost limit is exceeded."""

    def __init__(
        self,
        message: str = "Cost limit exceeded",
        current_cost: Optional[float] = None,
        limit: Optional[float] = None,
        limit_type: Optional[str] = None,
    ):
        details = {}
        if current_cost is not None:
            details['current_cost'] = current_cost
        if limit is not None:
            details['limit'] = limit
        if limit_type:
            details['limit_type'] = limit_type

        super().__init__(
            message=message,
            code="COST_LIMIT_ERROR",
            details=details,
        )


def handle_exception(e: Exception) -> Dict[str, Any]:
    """Convert any exception to a standardized error response."""
    if isinstance(e, BasementCowboyError):
        return e.to_dict()

    # Handle common built-in exceptions
    if isinstance(e, ValueError):
        return ValidationError(str(e)).to_dict()
    if isinstance(e, FileNotFoundError):
        return StorageError(str(e), operation="read").to_dict()
    if isinstance(e, PermissionError):
        return StorageError(str(e), operation="permission").to_dict()

    # Generic error
    return BasementCowboyError(
        message=str(e),
        code="INTERNAL_ERROR",
    ).to_dict()

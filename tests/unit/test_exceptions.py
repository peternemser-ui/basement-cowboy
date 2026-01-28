"""Tests for custom exceptions."""

import pytest
from app.utils.exceptions import (
    BasementCowboyError,
    ConfigurationError,
    ValidationError,
    APIError,
    ScraperError,
    RateLimitError,
    AuthenticationError,
    WordPressError,
    OpenAIError,
    StorageError,
    ArticleNotFoundError,
    DuplicateArticleError,
    CostLimitError,
    handle_exception
)


class TestBasementCowboyError:
    """Tests for base exception class."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = BasementCowboyError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.code == "UNKNOWN_ERROR"

    def test_error_with_code(self):
        """Test error with custom code."""
        error = BasementCowboyError("Error", code="CUSTOM_CODE")
        assert error.code == "CUSTOM_CODE"

    def test_error_with_details(self):
        """Test error with details."""
        error = BasementCowboyError("Error", details={"key": "value"})
        assert error.details == {"key": "value"}

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = BasementCowboyError("Test error", code="TEST", details={"foo": "bar"})
        result = error.to_dict()

        assert result['error']['code'] == "TEST"
        assert result['error']['message'] == "Test error"
        assert result['error']['details'] == {"foo": "bar"}


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_basic_config_error(self):
        """Test basic configuration error."""
        error = ConfigurationError("Missing API key")
        assert error.code == "CONFIGURATION_ERROR"
        assert "Missing API key" in str(error)

    def test_config_error_with_key(self):
        """Test configuration error with config key."""
        error = ConfigurationError("Missing key", config_key="OPENAI_API_KEY")
        assert error.details['config_key'] == "OPENAI_API_KEY"


class TestValidationError:
    """Tests for ValidationError."""

    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Invalid input")
        assert error.code == "VALIDATION_ERROR"

    def test_validation_error_with_field(self):
        """Test validation error with field."""
        error = ValidationError("Invalid email", field="email")
        assert error.details['field'] == "email"

    def test_validation_error_with_value(self):
        """Test validation error with value."""
        error = ValidationError("Invalid", field="url", value="not-a-url")
        assert error.details['value'] == "not-a-url"


class TestAPIError:
    """Tests for APIError."""

    def test_basic_api_error(self):
        """Test basic API error."""
        error = APIError("Request failed")
        assert error.code == "API_ERROR"

    def test_api_error_with_status(self):
        """Test API error with status code."""
        error = APIError("Not found", status_code=404)
        assert error.details['status_code'] == 404

    def test_api_error_with_api_name(self):
        """Test API error with API name."""
        error = APIError("Rate limited", api_name="OpenAI")
        assert error.details['api'] == "OpenAI"


class TestScraperError:
    """Tests for ScraperError."""

    def test_basic_scraper_error(self):
        """Test basic scraper error."""
        error = ScraperError("Failed to scrape")
        assert error.code == "SCRAPER_ERROR"

    def test_scraper_error_with_url(self):
        """Test scraper error with URL."""
        error = ScraperError("Timeout", url="https://example.com")
        assert error.details['url'] == "https://example.com"


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_basic_rate_limit_error(self):
        """Test basic rate limit error."""
        error = RateLimitError()
        assert error.code == "RATE_LIMIT_ERROR"
        assert "Rate limit" in str(error)

    def test_rate_limit_with_retry_after(self):
        """Test rate limit error with retry after."""
        error = RateLimitError(retry_after=60)
        assert error.details['retry_after'] == 60


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_basic_auth_error(self):
        """Test basic authentication error."""
        error = AuthenticationError()
        assert error.code == "AUTHENTICATION_ERROR"

    def test_auth_error_with_service(self):
        """Test authentication error with service."""
        error = AuthenticationError(service="WordPress")
        assert error.details['service'] == "WordPress"


class TestWordPressError:
    """Tests for WordPressError."""

    def test_basic_wordpress_error(self):
        """Test basic WordPress error."""
        error = WordPressError("Post creation failed")
        assert error.code == "WORDPRESS_ERROR"

    def test_wordpress_error_with_post_id(self):
        """Test WordPress error with post ID."""
        error = WordPressError("Update failed", operation="update", post_id=123)
        assert error.details['post_id'] == 123
        assert error.details['operation'] == "update"


class TestArticleErrors:
    """Tests for article-related errors."""

    def test_article_not_found(self):
        """Test ArticleNotFoundError."""
        error = ArticleNotFoundError("abc123")
        assert error.code == "ARTICLE_NOT_FOUND"
        assert "abc123" in str(error)
        assert error.details['article_id'] == "abc123"

    def test_duplicate_article(self):
        """Test DuplicateArticleError."""
        error = DuplicateArticleError("https://example.com/article", existing_id="xyz789")
        assert error.code == "DUPLICATE_ARTICLE"
        assert error.details['url'] == "https://example.com/article"
        assert error.details['existing_id'] == "xyz789"


class TestCostLimitError:
    """Tests for CostLimitError."""

    def test_basic_cost_limit_error(self):
        """Test basic cost limit error."""
        error = CostLimitError()
        assert error.code == "COST_LIMIT_ERROR"

    def test_cost_limit_with_details(self):
        """Test cost limit error with details."""
        error = CostLimitError(
            current_cost=55.50,
            limit=50.00,
            limit_type="daily"
        )
        assert error.details['current_cost'] == 55.50
        assert error.details['limit'] == 50.00
        assert error.details['limit_type'] == "daily"


class TestHandleException:
    """Tests for handle_exception function."""

    def test_handle_custom_exception(self):
        """Test handling custom exception."""
        error = ValidationError("Test", field="test")
        result = handle_exception(error)
        assert result['error']['code'] == "VALIDATION_ERROR"

    def test_handle_value_error(self):
        """Test handling ValueError."""
        error = ValueError("Invalid value")
        result = handle_exception(error)
        assert result['error']['code'] == "VALIDATION_ERROR"

    def test_handle_file_not_found(self):
        """Test handling FileNotFoundError."""
        error = FileNotFoundError("File missing")
        result = handle_exception(error)
        assert result['error']['code'] == "STORAGE_ERROR"

    def test_handle_generic_exception(self):
        """Test handling generic exception."""
        error = Exception("Something unexpected")
        result = handle_exception(error)
        assert result['error']['code'] == "INTERNAL_ERROR"

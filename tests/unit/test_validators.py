"""Tests for validator utilities."""

import pytest
from app.utils.validators import (
    validate_url, validate_email, validate_api_key,
    validate_article_title, validate_article_content,
    validate_positive_integer, validate_float_range,
    sanitize_filename, sanitize_html_attribute
)


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        is_valid, error = validate_url("http://example.com")
        assert is_valid
        assert error is None

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        is_valid, error = validate_url("https://example.com/path")
        assert is_valid
        assert error is None

    def test_missing_protocol(self):
        """Test URL without protocol."""
        is_valid, error = validate_url("example.com")
        assert not is_valid
        assert "protocol" in error.lower()

    def test_invalid_protocol(self):
        """Test invalid protocol."""
        is_valid, error = validate_url("ftp://example.com")
        assert not is_valid

    def test_empty_url(self):
        """Test empty URL."""
        is_valid, error = validate_url("")
        assert not is_valid
        assert "required" in error.lower()


class TestValidateEmail:
    """Tests for validate_email function."""

    def test_valid_email(self):
        """Test valid email."""
        is_valid, error = validate_email("user@example.com")
        assert is_valid
        assert error is None

    def test_invalid_email_no_at(self):
        """Test email without @."""
        is_valid, error = validate_email("userexample.com")
        assert not is_valid

    def test_invalid_email_no_domain(self):
        """Test email without domain."""
        is_valid, error = validate_email("user@")
        assert not is_valid

    def test_empty_email(self):
        """Test empty email."""
        is_valid, error = validate_email("")
        assert not is_valid


class TestValidateApiKey:
    """Tests for validate_api_key function."""

    def test_valid_openai_key(self):
        """Test valid OpenAI key format."""
        is_valid, error = validate_api_key("sk-" + "a" * 48, "openai")
        assert is_valid
        assert error is None

    def test_invalid_openai_key_prefix(self):
        """Test OpenAI key without sk- prefix."""
        is_valid, error = validate_api_key("invalid_key_format", "openai")
        assert not is_valid
        assert "sk-" in error

    def test_short_openai_key(self):
        """Test too short OpenAI key."""
        is_valid, error = validate_api_key("sk-short", "openai")
        assert not is_valid
        assert "short" in error.lower()

    def test_empty_key(self):
        """Test empty API key."""
        is_valid, error = validate_api_key("", "openai")
        assert not is_valid


class TestValidateArticleTitle:
    """Tests for validate_article_title function."""

    def test_valid_title(self):
        """Test valid article title."""
        is_valid, error = validate_article_title("This is a valid article title")
        assert is_valid

    def test_too_short_title(self):
        """Test too short title."""
        is_valid, error = validate_article_title("Short")
        assert not is_valid
        assert "short" in error.lower()

    def test_too_long_title(self):
        """Test too long title."""
        long_title = "A" * 201
        is_valid, error = validate_article_title(long_title)
        assert not is_valid
        assert "long" in error.lower()

    def test_clickbait_warning(self):
        """Test clickbait warning."""
        is_valid, error = validate_article_title("You Won't Believe What Happened")
        assert is_valid  # Still valid, just warning
        assert error and "clickbait" in error.lower()


class TestValidateArticleContent:
    """Tests for validate_article_content function."""

    def test_valid_content(self):
        """Test valid content."""
        content = "A" * 200
        is_valid, error = validate_article_content(content)
        assert is_valid

    def test_too_short_content(self):
        """Test too short content."""
        is_valid, error = validate_article_content("Short", min_length=100)
        assert not is_valid
        assert "short" in error.lower()

    def test_empty_content(self):
        """Test empty content."""
        is_valid, error = validate_article_content("")
        assert not is_valid


class TestValidatePositiveInteger:
    """Tests for validate_positive_integer function."""

    def test_valid_positive(self):
        """Test valid positive integer."""
        is_valid, error = validate_positive_integer(5)
        assert is_valid

    def test_zero(self):
        """Test zero."""
        is_valid, error = validate_positive_integer(0)
        assert not is_valid

    def test_negative(self):
        """Test negative number."""
        is_valid, error = validate_positive_integer(-5)
        assert not is_valid

    def test_string_number(self):
        """Test string that can be converted."""
        is_valid, error = validate_positive_integer("10")
        assert is_valid

    def test_invalid_string(self):
        """Test invalid string."""
        is_valid, error = validate_positive_integer("abc")
        assert not is_valid


class TestValidateFloatRange:
    """Tests for validate_float_range function."""

    def test_within_range(self):
        """Test value within range."""
        is_valid, error = validate_float_range(0.5, 0.0, 1.0)
        assert is_valid

    def test_below_range(self):
        """Test value below range."""
        is_valid, error = validate_float_range(-0.5, 0.0, 1.0)
        assert not is_valid

    def test_above_range(self):
        """Test value above range."""
        is_valid, error = validate_float_range(1.5, 0.0, 1.0)
        assert not is_valid

    def test_at_boundaries(self):
        """Test values at boundaries."""
        is_valid, _ = validate_float_range(0.0, 0.0, 1.0)
        assert is_valid
        is_valid, _ = validate_float_range(1.0, 0.0, 1.0)
        assert is_valid


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_basic_filename(self):
        """Test basic filename."""
        assert sanitize_filename("document.txt") == "document.txt"

    def test_unsafe_characters(self):
        """Test removing unsafe characters."""
        result = sanitize_filename("file<>:\"/\\|?*.txt")
        assert "<" not in result
        assert ">" not in result
        assert "*" not in result

    def test_long_filename(self):
        """Test truncating long filename."""
        long_name = "a" * 250 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 200


class TestSanitizeHtmlAttribute:
    """Tests for sanitize_html_attribute function."""

    def test_basic_text(self):
        """Test basic text."""
        assert sanitize_html_attribute("hello") == "hello"

    def test_special_characters(self):
        """Test escaping special characters."""
        result = sanitize_html_attribute('<script>alert("xss")</script>')
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result or "&quot;" in result

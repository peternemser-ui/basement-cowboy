"""Tests for HTTP utilities."""

import pytest
from app.utils.http import (
    get_domain, normalize_url, is_same_domain,
    make_absolute_url, get_random_user_agent,
    build_request_headers, parse_content_type,
    is_html_content, is_json_content, extract_links
)


class TestGetDomain:
    """Tests for get_domain function."""

    def test_basic_domain(self):
        """Test extracting basic domain."""
        assert get_domain("https://example.com/path") == "example.com"

    def test_domain_with_www(self):
        """Test stripping www prefix."""
        assert get_domain("https://www.example.com") == "example.com"

    def test_domain_with_subdomain(self):
        """Test preserving subdomain."""
        assert get_domain("https://blog.example.com") == "blog.example.com"

    def test_invalid_url(self):
        """Test handling invalid URL."""
        assert get_domain("not a url") == ""


class TestNormalizeUrl:
    """Tests for normalize_url function."""

    def test_lowercase_scheme(self):
        """Test lowercasing scheme."""
        normalized = normalize_url("HTTPS://Example.com")
        assert normalized.startswith("https://")

    def test_trailing_slash(self):
        """Test removing trailing slash."""
        normalized = normalize_url("https://example.com/path/")
        assert not normalized.endswith("/") or normalized.endswith("path")

    def test_query_params_sorted(self):
        """Test sorting query parameters."""
        url1 = normalize_url("https://example.com?b=2&a=1")
        url2 = normalize_url("https://example.com?a=1&b=2")
        assert url1 == url2


class TestIsSameDomain:
    """Tests for is_same_domain function."""

    def test_same_domain(self):
        """Test same domain detection."""
        assert is_same_domain(
            "https://example.com/page1",
            "https://example.com/page2"
        )

    def test_different_domain(self):
        """Test different domain detection."""
        assert not is_same_domain(
            "https://example.com",
            "https://other.com"
        )

    def test_subdomain_difference(self):
        """Test subdomain is considered different."""
        assert not is_same_domain(
            "https://www.example.com",
            "https://blog.example.com"
        )


class TestMakeAbsoluteUrl:
    """Tests for make_absolute_url function."""

    def test_relative_path(self):
        """Test converting relative path."""
        result = make_absolute_url("/page", "https://example.com")
        assert result == "https://example.com/page"

    def test_already_absolute(self):
        """Test already absolute URL unchanged."""
        url = "https://other.com/page"
        result = make_absolute_url(url, "https://example.com")
        assert result == url

    def test_relative_to_current(self):
        """Test relative to current path."""
        result = make_absolute_url("page2", "https://example.com/dir/page1")
        assert "page2" in result


class TestGetRandomUserAgent:
    """Tests for get_random_user_agent function."""

    def test_returns_string(self):
        """Test returns a string."""
        ua = get_random_user_agent()
        assert isinstance(ua, str)
        assert len(ua) > 20

    def test_contains_browser(self):
        """Test contains browser identifier."""
        ua = get_random_user_agent()
        assert any(browser in ua for browser in ['Chrome', 'Firefox', 'Safari', 'Edge'])


class TestBuildRequestHeaders:
    """Tests for build_request_headers function."""

    def test_default_headers(self):
        """Test default headers."""
        headers = build_request_headers()
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers

    def test_custom_user_agent(self):
        """Test custom user agent."""
        headers = build_request_headers(user_agent="CustomBot/1.0")
        assert headers['User-Agent'] == "CustomBot/1.0"

    def test_referer(self):
        """Test adding referer."""
        headers = build_request_headers(referer="https://google.com")
        assert headers['Referer'] == "https://google.com"

    def test_extra_headers(self):
        """Test extra headers."""
        headers = build_request_headers(extra_headers={'X-Custom': 'value'})
        assert headers['X-Custom'] == 'value'


class TestParseContentType:
    """Tests for parse_content_type function."""

    def test_simple_type(self):
        """Test parsing simple content type."""
        result = parse_content_type("text/html")
        assert result['type'] == "text/html"

    def test_with_charset(self):
        """Test parsing with charset."""
        result = parse_content_type("text/html; charset=utf-8")
        assert result['type'] == "text/html"
        assert result['charset'] == "utf-8"

    def test_empty_string(self):
        """Test empty string."""
        result = parse_content_type("")
        assert result['type'] == ""


class TestIsHtmlContent:
    """Tests for is_html_content function."""

    def test_html_type(self):
        """Test HTML content type."""
        assert is_html_content("text/html")
        assert is_html_content("text/html; charset=utf-8")

    def test_xhtml_type(self):
        """Test XHTML content type."""
        assert is_html_content("application/xhtml+xml")

    def test_non_html(self):
        """Test non-HTML content type."""
        assert not is_html_content("application/json")
        assert not is_html_content("text/plain")


class TestIsJsonContent:
    """Tests for is_json_content function."""

    def test_json_type(self):
        """Test JSON content type."""
        assert is_json_content("application/json")
        assert is_json_content("text/json")

    def test_non_json(self):
        """Test non-JSON content type."""
        assert not is_json_content("text/html")
        assert not is_json_content("text/plain")


class TestExtractLinks:
    """Tests for extract_links function."""

    def test_extract_absolute_links(self):
        """Test extracting absolute links."""
        html = '<a href="https://example.com/page1">Link</a>'
        links = extract_links(html, "https://base.com")
        assert "https://example.com/page1" in links

    def test_extract_relative_links(self):
        """Test extracting and converting relative links."""
        html = '<a href="/page">Link</a>'
        links = extract_links(html, "https://example.com")
        assert "https://example.com/page" in links

    def test_skip_special_links(self):
        """Test skipping special links."""
        html = '''
        <a href="javascript:void(0)">JS</a>
        <a href="mailto:test@example.com">Email</a>
        <a href="#section">Anchor</a>
        <a href="https://example.com">Valid</a>
        '''
        links = extract_links(html, "https://base.com")
        assert len(links) == 1
        assert "https://example.com" in links

    def test_deduplicate_links(self):
        """Test deduplicating links."""
        html = '''
        <a href="https://example.com">Link 1</a>
        <a href="https://example.com">Link 2</a>
        '''
        links = extract_links(html, "https://base.com")
        assert len(links) == 1

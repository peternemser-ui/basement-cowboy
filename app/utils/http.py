"""HTTP utilities."""

import time
import random
from typing import Optional, Dict, Any, Callable
from functools import wraps
from urllib.parse import urlparse, urljoin, parse_qs, urlencode


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    try:
        parsed = urlparse(url)

        # Lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Remove trailing slash from path
        path = parsed.path.rstrip('/')
        if not path:
            path = '/'

        # Sort query parameters
        query = parse_qs(parsed.query, keep_blank_values=True)
        sorted_query = urlencode(sorted(query.items()), doseq=True)

        # Reconstruct URL
        normalized = f"{scheme}://{netloc}{path}"
        if sorted_query:
            normalized += f"?{sorted_query}"

        return normalized
    except Exception:
        return url


def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs are from the same domain."""
    return get_domain(url1) == get_domain(url2)


def make_absolute_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute using base URL."""
    if url.startswith(('http://', 'https://')):
        return url
    return urljoin(base_url, url)


def get_user_agents() -> list:
    """Get a list of common user agents for rotation."""
    return [
        # Chrome on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Chrome on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # Firefox on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Firefox on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari on Mac
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        # Edge on Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]


def get_random_user_agent() -> str:
    """Get a random user agent string."""
    return random.choice(get_user_agents())


def retry_request(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for retrying failed requests with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        # Add jitter to prevent thundering herd
                        jitter = random.uniform(0, current_delay * 0.1)
                        time.sleep(current_delay + jitter)
                        current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, requests_per_second: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

    def __call__(self, func: Callable) -> Callable:
        """Use as decorator."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return func(*args, **kwargs)
        return wrapper


def build_request_headers(
    user_agent: Optional[str] = None,
    accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    accept_language: str = "en-US,en;q=0.5",
    referer: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Build standard request headers."""
    headers = {
        'User-Agent': user_agent or get_random_user_agent(),
        'Accept': accept,
        'Accept-Language': accept_language,
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    if referer:
        headers['Referer'] = referer

    if extra_headers:
        headers.update(extra_headers)

    return headers


def parse_content_type(content_type: str) -> Dict[str, str]:
    """Parse Content-Type header."""
    result = {'type': '', 'charset': 'utf-8'}

    if not content_type:
        return result

    parts = content_type.split(';')
    result['type'] = parts[0].strip()

    for part in parts[1:]:
        if '=' in part:
            key, value = part.split('=', 1)
            result[key.strip().lower()] = value.strip().strip('"')

    return result


def is_html_content(content_type: str) -> bool:
    """Check if content type is HTML."""
    parsed = parse_content_type(content_type)
    return parsed['type'] in ('text/html', 'application/xhtml+xml')


def is_json_content(content_type: str) -> bool:
    """Check if content type is JSON."""
    parsed = parse_content_type(content_type)
    return parsed['type'] in ('application/json', 'text/json')


def extract_links(html: str, base_url: str) -> list:
    """Extract all links from HTML content."""
    import re

    links = []
    pattern = r'href=["\']([^"\']+)["\']'

    for match in re.finditer(pattern, html, re.IGNORECASE):
        url = match.group(1)
        if not url.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
            absolute_url = make_absolute_url(url, base_url)
            links.append(absolute_url)

    return list(set(links))  # Remove duplicates

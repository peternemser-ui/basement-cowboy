"""Input validation utilities."""

import re
from typing import Optional, Tuple, List
from urllib.parse import urlparse


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate a URL. Returns (is_valid, error_message)."""
    if not url:
        return False, "URL is required"

    try:
        result = urlparse(url)

        # Must have scheme
        if not result.scheme:
            return False, "URL must include protocol (http:// or https://)"

        # Must be http or https
        if result.scheme not in ('http', 'https'):
            return False, "URL must use http or https protocol"

        # Must have netloc (domain)
        if not result.netloc:
            return False, "URL must include a domain"

        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, result.netloc.split(':')[0]):
            return False, "Invalid domain format"

        return True, None

    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate an email address. Returns (is_valid, error_message)."""
    if not email:
        return False, "Email is required"

    # Basic email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_api_key(key: str, provider: str = "openai") -> Tuple[bool, Optional[str]]:
    """Validate an API key format. Returns (is_valid, error_message)."""
    if not key:
        return False, "API key is required"

    if provider == "openai":
        # OpenAI keys start with "sk-" and are 51 characters
        if not key.startswith('sk-'):
            return False, "OpenAI API key must start with 'sk-'"
        if len(key) < 40:
            return False, "OpenAI API key appears too short"

    return True, None


def validate_wordpress_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate WordPress site URL. Returns (is_valid, error_message)."""
    is_valid, error = validate_url(url)
    if not is_valid:
        return is_valid, error

    # Check for common WordPress paths
    if url.endswith('/'):
        url = url[:-1]

    return True, None


def validate_json_string(json_str: str) -> Tuple[bool, Optional[str]]:
    """Validate JSON string. Returns (is_valid, error_message)."""
    if not json_str:
        return False, "JSON string is required"

    import json
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def validate_article_title(title: str) -> Tuple[bool, Optional[str]]:
    """Validate article title. Returns (is_valid, error_message)."""
    if not title:
        return False, "Title is required"

    if len(title) < 10:
        return False, "Title is too short (minimum 10 characters)"

    if len(title) > 200:
        return False, "Title is too long (maximum 200 characters)"

    # Check for clickbait indicators (warning, not error)
    clickbait_patterns = [
        r'You Won\'t Believe',
        r'This One Trick',
        r'Doctors Hate',
        r'!!!',
        r'\?\?\?',
    ]

    for pattern in clickbait_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            return True, f"Warning: Title may appear clickbaity"

    return True, None


def validate_article_content(content: str, min_length: int = 100) -> Tuple[bool, Optional[str]]:
    """Validate article content. Returns (is_valid, error_message)."""
    if not content:
        return False, "Content is required"

    if len(content) < min_length:
        return False, f"Content is too short (minimum {min_length} characters)"

    return True, None


def validate_category(category: str, allowed_categories: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate category against allowed list. Returns (is_valid, error_message)."""
    if not category:
        return False, "Category is required"

    if category not in allowed_categories:
        return False, f"Invalid category. Allowed: {', '.join(allowed_categories)}"

    return True, None


def validate_date_string(date_str: str, format: str = "%Y-%m-%d") -> Tuple[bool, Optional[str]]:
    """Validate date string format. Returns (is_valid, error_message)."""
    if not date_str:
        return False, "Date is required"

    from datetime import datetime
    try:
        datetime.strptime(date_str, format)
        return True, None
    except ValueError:
        return False, f"Invalid date format. Expected: {format}"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for filesystem."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')

    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')

    # Limit length
    if len(filename) > 200:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200-len(ext)-1] + '.' + ext if ext else name[:200]

    return filename or 'unnamed'


def sanitize_html_attribute(value: str) -> str:
    """Sanitize a value for use in HTML attributes."""
    import html
    return html.escape(value, quote=True)


def validate_positive_integer(value: any, name: str = "Value") -> Tuple[bool, Optional[str]]:
    """Validate positive integer. Returns (is_valid, error_message)."""
    try:
        int_val = int(value)
        if int_val <= 0:
            return False, f"{name} must be a positive integer"
        return True, None
    except (TypeError, ValueError):
        return False, f"{name} must be a valid integer"


def validate_float_range(
    value: any,
    min_val: float = 0.0,
    max_val: float = 1.0,
    name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """Validate float within range. Returns (is_valid, error_message)."""
    try:
        float_val = float(value)
        if float_val < min_val or float_val > max_val:
            return False, f"{name} must be between {min_val} and {max_val}"
        return True, None
    except (TypeError, ValueError):
        return False, f"{name} must be a valid number"

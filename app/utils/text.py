"""Text processing utilities."""

import re
import html
from typing import Optional


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug."""
    # Convert to lowercase
    slug = text.lower()

    # Replace accented characters
    replacements = {
        'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
        'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
        'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
        'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
        'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
        'ñ': 'n', 'ç': 'c',
    }
    for char, replacement in replacements.items():
        slug = slug.replace(char, replacement)

    # Remove non-alphanumeric characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)

    # Replace whitespace and multiple dashes with single dash
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing dashes
    slug = slug.strip('-')

    # Truncate at word boundary if too long
    if len(slug) > max_length:
        slug = slug[:max_length]
        last_dash = slug.rfind('-')
        if last_dash > max_length - 15:
            slug = slug[:last_dash]

    return slug


def truncate(text: str, max_length: int = 160, suffix: str = '...') -> str:
    """Truncate text to max length, preserving word boundaries."""
    if len(text) <= max_length:
        return text

    # Account for suffix length
    target_length = max_length - len(suffix)

    truncated = text[:target_length]

    # Try to cut at word boundary
    last_space = truncated.rfind(' ')
    if last_space > target_length - 20:
        truncated = truncated[:last_space]

    return truncated.rstrip() + suffix


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    # Decode HTML entities first
    text = html.unescape(text)

    # Remove script and style elements entirely
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Normalize whitespace
    text = normalize_whitespace(text)

    return text


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove leading/trailing whitespace from lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def extract_first_paragraph(text: str) -> str:
    """Extract first paragraph from text."""
    # Split by double newline (paragraph break)
    paragraphs = re.split(r'\n\s*\n', text)

    for p in paragraphs:
        p = p.strip()
        if len(p) > 50:  # Skip very short paragraphs
            return p

    return paragraphs[0] if paragraphs else ''


def word_count(text: str) -> int:
    """Count words in text."""
    words = re.findall(r'\b\w+\b', text)
    return len(words)


def sentence_count(text: str) -> int:
    """Count sentences in text."""
    # Split on sentence-ending punctuation
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)


def reading_time_minutes(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes."""
    words = word_count(text)
    minutes = words / words_per_minute
    return max(1, round(minutes))


def extract_sentences(text: str, count: int = 3) -> str:
    """Extract first N sentences from text."""
    # Find sentence boundaries
    sentence_pattern = r'(?<=[.!?])\s+'
    sentences = re.split(sentence_pattern, text)

    # Take first N sentences
    selected = sentences[:count]

    # Ensure proper ending
    result = ' '.join(selected)
    if result and result[-1] not in '.!?':
        result += '.'

    return result


def highlight_keywords(text: str, keywords: list, tag: str = 'mark') -> str:
    """Wrap keywords in HTML tags for highlighting."""
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'<{tag}>\\g<0></{tag}>', text)
    return text


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
    return re.sub(url_pattern, '', text)


def clean_article_content(text: str) -> str:
    """Clean article content for display."""
    # Strip HTML
    text = strip_html(text)

    # Remove URLs
    text = remove_urls(text)

    # Normalize whitespace
    text = normalize_whitespace(text)

    # Remove common boilerplate patterns
    boilerplate_patterns = [
        r'Subscribe to our newsletter.*',
        r'Follow us on (Twitter|Facebook|Instagram).*',
        r'Share this article.*',
        r'Related articles?:.*',
        r'Read more:.*',
        r'Click here to.*',
        r'Sign up for.*',
    ]

    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


def is_english(text: str, threshold: float = 0.7) -> bool:
    """Check if text is likely English based on common words."""
    common_english = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    }

    words = re.findall(r'\b[a-z]+\b', text.lower())
    if not words:
        return False

    english_words = sum(1 for w in words if w in common_english)
    ratio = english_words / len(words)

    return ratio >= threshold

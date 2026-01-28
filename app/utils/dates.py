"""Date and time utilities."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Union


def parse_date(date_string: str) -> Optional[datetime]:
    """Parse various date string formats into datetime."""
    if not date_string:
        return None

    # Common date formats to try
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds
        "%Y-%m-%dT%H:%M:%SZ",     # ISO 8601
        "%Y-%m-%dT%H:%M:%S%z",    # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S",      # ISO 8601 without timezone
        "%Y-%m-%d %H:%M:%S",      # Standard datetime
        "%Y-%m-%d",               # Date only
        "%d/%m/%Y %H:%M:%S",      # European format
        "%d/%m/%Y",               # European date
        "%m/%d/%Y %H:%M:%S",      # US format
        "%m/%d/%Y",               # US date
        "%B %d, %Y",              # Month day, year
        "%b %d, %Y",              # Abbreviated month
        "%d %B %Y",               # Day month year
        "%d %b %Y",               # Day abbreviated month year
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string.strip(), fmt)
        except ValueError:
            continue

    # Try relative date parsing
    relative = parse_relative_date(date_string)
    if relative:
        return relative

    return None


def parse_relative_date(text: str) -> Optional[datetime]:
    """Parse relative date strings like '2 hours ago'."""
    text = text.lower().strip()
    now = datetime.now()

    patterns = [
        (r'(\d+)\s*seconds?\s*ago', lambda m: now - timedelta(seconds=int(m.group(1)))),
        (r'(\d+)\s*minutes?\s*ago', lambda m: now - timedelta(minutes=int(m.group(1)))),
        (r'(\d+)\s*hours?\s*ago', lambda m: now - timedelta(hours=int(m.group(1)))),
        (r'(\d+)\s*days?\s*ago', lambda m: now - timedelta(days=int(m.group(1)))),
        (r'(\d+)\s*weeks?\s*ago', lambda m: now - timedelta(weeks=int(m.group(1)))),
        (r'(\d+)\s*months?\s*ago', lambda m: now - timedelta(days=int(m.group(1)) * 30)),
        (r'(\d+)\s*years?\s*ago', lambda m: now - timedelta(days=int(m.group(1)) * 365)),
        (r'yesterday', lambda m: now - timedelta(days=1)),
        (r'today', lambda m: now),
        (r'just\s*now', lambda m: now),
    ]

    for pattern, handler in patterns:
        match = re.search(pattern, text)
        if match:
            return handler(match)

    return None


def format_relative(dt: datetime, now: Optional[datetime] = None) -> str:
    """Format datetime as relative time string."""
    if now is None:
        now = datetime.now()

    # Handle timezone-aware datetimes
    if dt.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=dt.tzinfo)
    elif dt.tzinfo is None and now.tzinfo is not None:
        dt = dt.replace(tzinfo=now.tzinfo)

    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 0:
        return "in the future"

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def is_recent(dt: datetime, hours: int = 24) -> bool:
    """Check if datetime is within the specified hours."""
    if dt is None:
        return False

    now = datetime.now()

    # Handle timezone-aware datetimes
    if dt.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=dt.tzinfo)

    age = now - dt
    return age.total_seconds() < hours * 3600


def is_today(dt: datetime) -> bool:
    """Check if datetime is today."""
    return dt.date() == datetime.now().date()


def is_this_week(dt: datetime) -> bool:
    """Check if datetime is within the current week."""
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    return dt.date() >= start_of_week.date()


def format_date(dt: datetime, format: str = "medium") -> str:
    """Format datetime according to predefined format."""
    formats = {
        "short": "%m/%d/%y",
        "medium": "%b %d, %Y",
        "long": "%B %d, %Y",
        "full": "%A, %B %d, %Y",
        "iso": "%Y-%m-%d",
        "datetime": "%Y-%m-%d %H:%M:%S",
        "time": "%H:%M",
        "time_full": "%H:%M:%S",
    }

    fmt = formats.get(format, format)
    return dt.strftime(fmt)


def get_date_range(period: str) -> tuple:
    """Get start and end dates for common periods."""
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    ranges = {
        "today": (today, now),
        "yesterday": (today - timedelta(days=1), today),
        "this_week": (today - timedelta(days=today.weekday()), now),
        "last_week": (
            today - timedelta(days=today.weekday() + 7),
            today - timedelta(days=today.weekday())
        ),
        "this_month": (today.replace(day=1), now),
        "last_month": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1)
        ),
        "last_7_days": (today - timedelta(days=7), now),
        "last_30_days": (today - timedelta(days=30), now),
        "last_90_days": (today - timedelta(days=90), now),
    }

    return ranges.get(period, (today, now))


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC."""
    if dt.tzinfo is None:
        # Assume local time
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def from_timestamp(timestamp: Union[int, float]) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(timestamp)


def to_timestamp(dt: datetime) -> float:
    """Convert datetime to Unix timestamp."""
    return dt.timestamp()


def get_age_in_hours(dt: datetime) -> float:
    """Get age of datetime in hours."""
    now = datetime.now()
    if dt.tzinfo is not None and now.tzinfo is None:
        now = now.replace(tzinfo=dt.tzinfo)
    diff = now - dt
    return diff.total_seconds() / 3600

"""Tests for date utilities."""

import pytest
from datetime import datetime, timedelta
from app.utils.dates import (
    parse_date, parse_relative_date, format_relative,
    is_recent, is_today, is_this_week, format_date,
    get_date_range, get_age_in_hours
)


class TestParseDate:
    """Tests for parse_date function."""

    def test_iso_format(self):
        """Test ISO 8601 format."""
        result = parse_date("2024-01-15T10:30:00")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_iso_format_with_z(self):
        """Test ISO 8601 with Z suffix."""
        result = parse_date("2024-01-15T10:30:00Z")
        assert result is not None

    def test_date_only(self):
        """Test date only format."""
        result = parse_date("2024-01-15")
        assert result.year == 2024

    def test_european_format(self):
        """Test European date format."""
        result = parse_date("15/01/2024")
        assert result.day == 15

    def test_us_format(self):
        """Test US date format."""
        result = parse_date("01/15/2024")
        assert result is not None

    def test_written_format(self):
        """Test written date format."""
        result = parse_date("January 15, 2024")
        assert result is not None

    def test_invalid_format(self):
        """Test invalid format returns None."""
        result = parse_date("not a date")
        assert result is None

    def test_empty_string(self):
        """Test empty string returns None."""
        result = parse_date("")
        assert result is None


class TestParseRelativeDate:
    """Tests for parse_relative_date function."""

    def test_hours_ago(self):
        """Test parsing hours ago."""
        result = parse_relative_date("2 hours ago")
        assert result is not None
        age = datetime.now() - result
        assert 1.9 < age.total_seconds() / 3600 < 2.1

    def test_minutes_ago(self):
        """Test parsing minutes ago."""
        result = parse_relative_date("30 minutes ago")
        assert result is not None

    def test_days_ago(self):
        """Test parsing days ago."""
        result = parse_relative_date("3 days ago")
        assert result is not None

    def test_yesterday(self):
        """Test parsing yesterday."""
        result = parse_relative_date("yesterday")
        assert result is not None
        assert result.date() == (datetime.now() - timedelta(days=1)).date()

    def test_just_now(self):
        """Test parsing just now."""
        result = parse_relative_date("just now")
        assert result is not None
        assert (datetime.now() - result).total_seconds() < 5


class TestFormatRelative:
    """Tests for format_relative function."""

    def test_just_now(self):
        """Test formatting very recent time."""
        dt = datetime.now() - timedelta(seconds=30)
        assert format_relative(dt) == "just now"

    def test_minutes_ago(self):
        """Test formatting minutes ago."""
        dt = datetime.now() - timedelta(minutes=5)
        assert "5 minute" in format_relative(dt)

    def test_hours_ago(self):
        """Test formatting hours ago."""
        dt = datetime.now() - timedelta(hours=3)
        assert "3 hour" in format_relative(dt)

    def test_days_ago(self):
        """Test formatting days ago."""
        dt = datetime.now() - timedelta(days=2)
        assert "2 day" in format_relative(dt)

    def test_weeks_ago(self):
        """Test formatting weeks ago."""
        dt = datetime.now() - timedelta(weeks=2)
        assert "2 week" in format_relative(dt)


class TestIsRecent:
    """Tests for is_recent function."""

    def test_recent_article(self):
        """Test recent article."""
        dt = datetime.now() - timedelta(hours=12)
        assert is_recent(dt, hours=24)

    def test_old_article(self):
        """Test old article."""
        dt = datetime.now() - timedelta(days=3)
        assert not is_recent(dt, hours=24)

    def test_none_datetime(self):
        """Test None datetime."""
        assert not is_recent(None)


class TestIsToday:
    """Tests for is_today function."""

    def test_today(self):
        """Test today's date."""
        assert is_today(datetime.now())

    def test_yesterday(self):
        """Test yesterday."""
        dt = datetime.now() - timedelta(days=1)
        assert not is_today(dt)


class TestIsThisWeek:
    """Tests for is_this_week function."""

    def test_this_week(self):
        """Test date this week."""
        assert is_this_week(datetime.now())

    def test_last_week(self):
        """Test date last week."""
        dt = datetime.now() - timedelta(days=10)
        assert not is_this_week(dt)


class TestFormatDate:
    """Tests for format_date function."""

    def test_short_format(self):
        """Test short format."""
        dt = datetime(2024, 1, 15)
        result = format_date(dt, "short")
        assert "/" in result

    def test_medium_format(self):
        """Test medium format."""
        dt = datetime(2024, 1, 15)
        result = format_date(dt, "medium")
        assert "Jan" in result

    def test_long_format(self):
        """Test long format."""
        dt = datetime(2024, 1, 15)
        result = format_date(dt, "long")
        assert "January" in result

    def test_iso_format(self):
        """Test ISO format."""
        dt = datetime(2024, 1, 15)
        result = format_date(dt, "iso")
        assert result == "2024-01-15"


class TestGetDateRange:
    """Tests for get_date_range function."""

    def test_today_range(self):
        """Test today range."""
        start, end = get_date_range("today")
        assert start.date() == datetime.now().date()

    def test_last_7_days(self):
        """Test last 7 days range."""
        start, end = get_date_range("last_7_days")
        assert (end - start).days >= 7

    def test_last_30_days(self):
        """Test last 30 days range."""
        start, end = get_date_range("last_30_days")
        assert (end - start).days >= 30


class TestGetAgeInHours:
    """Tests for get_age_in_hours function."""

    def test_hours_calculation(self):
        """Test hours calculation."""
        dt = datetime.now() - timedelta(hours=5)
        age = get_age_in_hours(dt)
        assert 4.9 < age < 5.1

    def test_days_to_hours(self):
        """Test days converted to hours."""
        dt = datetime.now() - timedelta(days=2)
        age = get_age_in_hours(dt)
        assert 47 < age < 49

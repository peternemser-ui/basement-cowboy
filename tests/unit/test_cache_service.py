"""Tests for CacheService."""

import pytest
import tempfile
import shutil
import time
from pathlib import Path

from app.services.cache_service import MemoryCache, FileCache, CacheService


class TestMemoryCache:
    """Tests for MemoryCache."""

    @pytest.fixture
    def cache(self):
        """Create memory cache with short TTL for testing."""
        return MemoryCache(max_size=10, default_ttl=2)

    def test_set_and_get(self, cache):
        """Test basic set and get."""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key."""
        assert cache.get("nonexistent") is None

    def test_expiration(self, cache):
        """Test cache expiration."""
        cache.set("expire_key", "value", ttl=1)
        assert cache.get("expire_key") == "value"

        time.sleep(1.5)
        assert cache.get("expire_key") is None

    def test_delete(self, cache):
        """Test deleting cache entry."""
        cache.set("del_key", "value")
        assert cache.delete("del_key")
        assert cache.get("del_key") is None

    def test_clear(self, cache):
        """Test clearing cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        count = cache.clear()
        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_max_size_eviction(self, cache):
        """Test eviction when max size is reached."""
        for i in range(15):
            cache.set(f"key{i}", f"value{i}")

        # Should have evicted some entries
        stats = cache.get_stats()
        assert stats['total_entries'] <= 10

    def test_stats(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")
        cache.get("key1")

        stats = cache.get_stats()
        assert stats['total_entries'] == 2
        assert stats['total_hits'] >= 2


class TestFileCache:
    """Tests for FileCache."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for file cache."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def cache(self, temp_dir):
        """Create file cache."""
        return FileCache(cache_dir=temp_dir, default_ttl=300)

    def test_set_and_get(self, cache):
        """Test basic set and get."""
        cache.set("file_key", {"data": "test"})
        result = cache.get("file_key")
        assert result == {"data": "test"}

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key."""
        assert cache.get("nonexistent") is None

    def test_delete(self, cache):
        """Test deleting cache entry."""
        cache.set("del_key", "value")
        assert cache.delete("del_key")
        assert cache.get("del_key") is None

    def test_clear(self, cache):
        """Test clearing cache."""
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        count = cache.clear()
        assert count == 2

    def test_complex_data(self, cache):
        """Test caching complex data structures."""
        data = {
            "list": [1, 2, 3],
            "nested": {"a": "b"},
            "number": 42,
        }
        cache.set("complex", data)
        result = cache.get("complex")
        assert result == data


class TestCacheService:
    """Tests for CacheService."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def service(self, temp_dir):
        """Create cache service."""
        return CacheService(
            memory_max_size=100,
            memory_ttl=60,
            file_cache_dir=temp_dir,
            file_ttl=300,
        )

    def test_memory_only(self, service):
        """Test memory-only caching."""
        service.set("mem_key", "value")
        assert service.get("mem_key") == "value"

    def test_persistent_cache(self, service):
        """Test persistent caching."""
        service.set("persist_key", "value", persist=True)
        assert service.get("persist_key", use_file=True) == "value"

    def test_clear_all(self, service):
        """Test clearing all caches."""
        service.set("key1", "value1")
        service.set("key2", "value2", persist=True)

        stats = service.clear_all()
        assert stats['memory'] >= 1

    def test_stats(self, service):
        """Test combined stats."""
        service.set("key1", "value1")
        service.set("key2", "value2", persist=True)

        stats = service.get_stats()
        assert 'memory' in stats
        assert 'file' in stats

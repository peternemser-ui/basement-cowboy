"""Caching service."""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable, TypeVar
from pathlib import Path
from functools import wraps
from threading import Lock

T = TypeVar('T')


class CacheEntry:
    """Single cache entry with expiration."""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)
        self.hits = 0

    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.created_at + self.ttl

    def touch(self) -> None:
        """Record a cache hit."""
        self.hits += 1


class MemoryCache:
    """In-memory cache with TTL support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                entry.touch()
                return entry.value
            elif entry:
                # Remove expired entry
                del self._cache[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self._lock:
            # Enforce max size
            if len(self._cache) >= self.max_size:
                self._evict_oldest()

            ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """Clear all entries. Returns count of cleared entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def _evict_oldest(self) -> None:
        """Evict oldest entries to make room."""
        # Remove expired entries first
        expired = [k for k, v in self._cache.items() if v.is_expired]
        for key in expired:
            del self._cache[key]

        # If still over limit, remove least recently used
        if len(self._cache) >= self.max_size:
            # Sort by hits (least used first)
            sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k].hits)
            # Remove bottom 10%
            to_remove = max(1, len(sorted_keys) // 10)
            for key in sorted_keys[:to_remove]:
                del self._cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for e in self._cache.values() if e.is_expired)
            total_hits = sum(e.hits for e in self._cache.values())

            return {
                'total_entries': total,
                'expired_entries': expired,
                'active_entries': total - expired,
                'total_hits': total_hits,
                'max_size': self.max_size,
                'utilization': total / self.max_size if self.max_size > 0 else 0,
            }


class FileCache:
    """File-based cache for persistence across restarts."""

    def __init__(self, cache_dir: str = "output/cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _get_path(self, key: str) -> Path:
        """Get file path for cache key."""
        # Hash key to create safe filename
        hashed = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get value from file cache."""
        path = self._get_path(key)
        if not path.exists():
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check expiration
            expires_at = datetime.fromisoformat(data['expires_at'])
            if datetime.now() > expires_at:
                path.unlink()
                return None

            return data['value']
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in file cache."""
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)

        data = {
            'key': key,
            'value': value,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
        }

        path = self._get_path(key)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        except Exception:
            pass

    def delete(self, key: str) -> bool:
        """Delete from file cache."""
        path = self._get_path(key)
        try:
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def clear(self) -> int:
        """Clear all cache files."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except Exception:
                pass
        return count

    def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expires_at:
                    f.unlink()
                    count += 1
            except Exception:
                # Invalid cache file, remove it
                try:
                    f.unlink()
                    count += 1
                except Exception:
                    pass
        return count


class CacheService:
    """Unified caching service with multiple backends."""

    def __init__(
        self,
        memory_max_size: int = 1000,
        memory_ttl: int = 300,
        file_cache_dir: str = "output/cache",
        file_ttl: int = 3600,
    ):
        self.memory = MemoryCache(max_size=memory_max_size, default_ttl=memory_ttl)
        self.file = FileCache(cache_dir=file_cache_dir, default_ttl=file_ttl)

    def get(self, key: str, use_file: bool = False) -> Optional[Any]:
        """Get from cache, trying memory first."""
        # Try memory cache first
        value = self.memory.get(key)
        if value is not None:
            return value

        # Try file cache if enabled
        if use_file:
            value = self.file.get(key)
            if value is not None:
                # Promote to memory cache
                self.memory.set(key, value)
                return value

        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        persist: bool = False,
    ) -> None:
        """Set in cache."""
        self.memory.set(key, value, ttl)
        if persist:
            self.file.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete from all caches."""
        mem_deleted = self.memory.delete(key)
        file_deleted = self.file.delete(key)
        return mem_deleted or file_deleted

    def clear_all(self) -> Dict[str, int]:
        """Clear all caches."""
        return {
            'memory': self.memory.clear(),
            'file': self.file.clear(),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics."""
        return {
            'memory': self.memory.get_stats(),
            'file': {
                'entries': len(list(self.file.cache_dir.glob("*.json"))),
            },
        }


def cached(
    cache: CacheService,
    key_prefix: str = "",
    ttl: int = 300,
    persist: bool = False,
) -> Callable:
    """Decorator for caching function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Build cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            # Try cache
            result = cache.get(cache_key, use_file=persist)
            if result is not None:
                return result

            # Call function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl=ttl, persist=persist)

            return result
        return wrapper
    return decorator

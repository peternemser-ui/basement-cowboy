"""Storage abstraction service."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TypeVar, Generic
from abc import ABC, abstractmethod


T = TypeVar('T')


class StorageBackend(ABC, Generic[T]):
    """Abstract storage backend."""

    @abstractmethod
    def save(self, key: str, data: T) -> bool:
        """Save data with key."""
        pass

    @abstractmethod
    def load(self, key: str) -> Optional[T]:
        """Load data by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def list_keys(self) -> List[str]:
        """List all keys."""
        pass


class FileStorageBackend(StorageBackend[Dict[str, Any]]):
    """File-based JSON storage backend."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        """Get file path for key."""
        return self.base_path / f"{key}.json"

    def save(self, key: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file."""
        try:
            file_path = self._get_path(key)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Storage save error: {e}")
            return False

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            file_path = self._get_path(key)
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Storage load error: {e}")
        return None

    def delete(self, key: str) -> bool:
        """Delete JSON file."""
        try:
            file_path = self._get_path(key)
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Storage delete error: {e}")
        return False

    def exists(self, key: str) -> bool:
        """Check if file exists."""
        return self._get_path(key).exists()

    def list_keys(self) -> List[str]:
        """List all keys (file names without extension)."""
        return [f.stem for f in self.base_path.glob("*.json")]

    def get_all(self) -> List[Dict[str, Any]]:
        """Load all stored items."""
        items = []
        for key in self.list_keys():
            data = self.load(key)
            if data:
                items.append(data)
        return items

    def count(self) -> int:
        """Count stored items."""
        return len(list(self.base_path.glob("*.json")))

    def clear(self) -> int:
        """Delete all stored items. Returns count of deleted items."""
        deleted = 0
        for f in self.base_path.glob("*.json"):
            try:
                f.unlink()
                deleted += 1
            except Exception:
                pass
        return deleted


class StorageService:
    """Main storage service with multiple backends."""

    def __init__(self, base_path: str = "output"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize storage backends for different data types
        self.articles = FileStorageBackend(self.base_path / "news_articles")
        self.wordpress = FileStorageBackend(self.base_path / "wordpress-output")
        self.logs = FileStorageBackend(self.base_path / "logs")
        self.cache = FileStorageBackend(self.base_path / "cache")

    def get_backend(self, name: str) -> FileStorageBackend:
        """Get or create a storage backend by name."""
        path = self.base_path / name
        path.mkdir(parents=True, exist_ok=True)
        return FileStorageBackend(path)

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'articles': self.articles.count(),
            'wordpress_posts': self.wordpress.count(),
            'log_files': self.logs.count(),
            'cache_entries': self.cache.count(),
            'total_size_mb': self._get_directory_size() / (1024 * 1024),
        }
        return stats

    def _get_directory_size(self) -> int:
        """Get total directory size in bytes."""
        total = 0
        for path in self.base_path.rglob('*'):
            if path.is_file():
                total += path.stat().st_size
        return total

    def backup(self, backup_path: str) -> bool:
        """Create a backup of all storage."""
        try:
            backup_dir = Path(backup_path)
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(self.base_path, backup_dir)
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False

    def restore(self, backup_path: str) -> bool:
        """Restore from a backup."""
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                return False

            # Clear current storage
            if self.base_path.exists():
                shutil.rmtree(self.base_path)

            # Copy backup
            shutil.copytree(backup_dir, self.base_path)
            return True
        except Exception as e:
            print(f"Restore error: {e}")
            return False

    def cleanup_old(self, days: int = 7) -> Dict[str, int]:
        """Remove files older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cleaned = {
            'articles': 0,
            'cache': 0,
            'logs': 0,
        }

        # Clean articles
        for f in (self.base_path / "news_articles").glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                cleaned['articles'] += 1

        # Clean cache
        for f in (self.base_path / "cache").glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                cleaned['cache'] += 1

        # Clean old logs
        for f in (self.base_path / "logs").glob("*.json"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                cleaned['logs'] += 1

        return cleaned

    def export_articles(self, output_file: str, format: str = "json") -> bool:
        """Export all articles to a single file."""
        try:
            articles = self.articles.get_all()

            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=2, ensure_ascii=False)
            elif format == "jsonl":
                with open(output_file, 'w', encoding='utf-8') as f:
                    for article in articles:
                        f.write(json.dumps(article, ensure_ascii=False) + '\n')
            else:
                return False

            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

    def import_articles(self, input_file: str) -> int:
        """Import articles from a file. Returns count of imported articles."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            # Try JSON array first
            if content.startswith('['):
                articles = json.loads(content)
            else:
                # Try JSONL
                articles = [json.loads(line) for line in content.split('\n') if line.strip()]

            imported = 0
            for article in articles:
                key = article.get('id')
                if key and self.articles.save(key, article):
                    imported += 1

            return imported
        except Exception as e:
            print(f"Import error: {e}")
            return 0

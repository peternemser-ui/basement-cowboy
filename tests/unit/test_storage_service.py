"""Tests for StorageService."""

import pytest
import tempfile
import shutil
from pathlib import Path

from app.services.storage_service import StorageService, FileStorageBackend


class TestFileStorageBackend:
    """Tests for FileStorageBackend."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def backend(self, temp_dir):
        """Create storage backend."""
        return FileStorageBackend(temp_dir)

    def test_save_and_load(self, backend):
        """Test saving and loading data."""
        data = {"title": "Test", "content": "Content"}
        assert backend.save("test_key", data)

        loaded = backend.load("test_key")
        assert loaded == data

    def test_load_nonexistent(self, backend):
        """Test loading nonexistent key."""
        assert backend.load("nonexistent") is None

    def test_exists(self, backend):
        """Test checking existence."""
        backend.save("exists_key", {"data": "test"})

        assert backend.exists("exists_key")
        assert not backend.exists("not_exists")

    def test_delete(self, backend):
        """Test deleting data."""
        backend.save("del_key", {"data": "test"})
        assert backend.exists("del_key")

        assert backend.delete("del_key")
        assert not backend.exists("del_key")

    def test_list_keys(self, backend):
        """Test listing keys."""
        backend.save("key1", {"data": 1})
        backend.save("key2", {"data": 2})
        backend.save("key3", {"data": 3})

        keys = backend.list_keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys

    def test_get_all(self, backend):
        """Test getting all items."""
        backend.save("item1", {"id": 1})
        backend.save("item2", {"id": 2})

        items = backend.get_all()
        assert len(items) == 2

    def test_count(self, backend):
        """Test counting items."""
        assert backend.count() == 0

        backend.save("item1", {"data": 1})
        backend.save("item2", {"data": 2})

        assert backend.count() == 2

    def test_clear(self, backend):
        """Test clearing all items."""
        backend.save("item1", {"data": 1})
        backend.save("item2", {"data": 2})

        deleted = backend.clear()
        assert deleted == 2
        assert backend.count() == 0


class TestStorageService:
    """Tests for StorageService."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def service(self, temp_dir):
        """Create storage service."""
        return StorageService(base_path=temp_dir)

    def test_articles_backend(self, service):
        """Test articles backend."""
        service.articles.save("article1", {"title": "Test"})
        assert service.articles.load("article1") == {"title": "Test"}

    def test_get_backend(self, service):
        """Test getting custom backend."""
        custom = service.get_backend("custom")
        custom.save("key", {"data": "test"})
        assert custom.load("key") == {"data": "test"}

    def test_storage_stats(self, service):
        """Test storage statistics."""
        service.articles.save("a1", {"data": 1})
        service.articles.save("a2", {"data": 2})
        service.cache.save("c1", {"cached": True})

        stats = service.get_storage_stats()
        assert stats['articles'] == 2
        assert stats['cache_entries'] == 1

    def test_backup_and_restore(self, service, temp_dir):
        """Test backup and restore."""
        # Save some data
        service.articles.save("article1", {"title": "Test 1"})
        service.articles.save("article2", {"title": "Test 2"})

        # Create backup
        backup_path = Path(temp_dir) / "backup"
        assert service.backup(str(backup_path))

        # Clear data
        service.articles.clear()
        assert service.articles.count() == 0

        # Restore
        assert service.restore(str(backup_path))

    def test_export_import_articles(self, service, temp_dir):
        """Test exporting and importing articles."""
        # Save articles
        service.articles.save("a1", {"id": "a1", "title": "Article 1"})
        service.articles.save("a2", {"id": "a2", "title": "Article 2"})

        # Export
        export_file = Path(temp_dir) / "export.json"
        assert service.export_articles(str(export_file))

        # Clear
        service.articles.clear()

        # Import
        imported = service.import_articles(str(export_file))
        assert imported == 2
        assert service.articles.count() == 2

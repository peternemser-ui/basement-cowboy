"""Tests for ArticleService."""

import pytest
import tempfile
import shutil
from pathlib import Path

from app.services.article_service import ArticleService
from app.models.article import Article, ArticleStatus, ArticleSource


class TestArticleService:
    """Tests for ArticleService."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def service(self, temp_storage):
        """Create ArticleService with temp storage."""
        return ArticleService(storage_path=temp_storage)

    @pytest.fixture
    def sample_source(self):
        """Create sample ArticleSource."""
        return ArticleSource(
            name="Test Source",
            url="https://testsource.com",
            domain="testsource.com",
        )

    def test_generate_id(self, service):
        """Test ID generation from URL."""
        id1 = service.generate_id("https://example.com/article1")
        id2 = service.generate_id("https://example.com/article2")
        id3 = service.generate_id("https://example.com/article1")

        assert id1 != id2
        assert id1 == id3  # Same URL should produce same ID

    def test_create_article(self, service):
        """Test creating an article."""
        article = service.create(
            title="Test Article",
            url="https://example.com/test",
            source_name="Example",
            source_url="https://example.com",
            content="This is test content.",
        )

        assert article.title == "Test Article"
        assert article.source.name == "Example"
        assert article.is_valid()

    def test_save_and_get(self, service, sample_source):
        """Test saving and retrieving an article."""
        article = Article(
            id="test123",
            title="Save Test",
            url="https://example.com/save",
            source=sample_source,
            content="Content here",
        )

        assert service.save(article)

        retrieved = service.get("test123")
        assert retrieved is not None
        assert retrieved.title == "Save Test"
        assert retrieved.source.name == "Test Source"

    def test_get_nonexistent(self, service):
        """Test getting a non-existent article."""
        result = service.get("nonexistent")
        assert result is None

    def test_get_all(self, service, sample_source):
        """Test getting all articles."""
        for i in range(3):
            article = Article(
                id=f"article{i}",
                title=f"Article {i}",
                url=f"https://example.com/{i}",
                source=sample_source,
            )
            service.save(article)

        articles = service.get_all()
        assert len(articles) == 3

    def test_get_by_status(self, service, sample_source):
        """Test filtering articles by status."""
        article1 = Article(
            id="a1", title="Article 1",
            url="https://example.com/1",
            source=sample_source,
            status=ArticleStatus.SCRAPED,
        )
        article2 = Article(
            id="a2", title="Article 2",
            url="https://example.com/2",
            source=sample_source,
            status=ArticleStatus.PUBLISHED,
        )

        service.save(article1)
        service.save(article2)

        scraped = service.get_all(status=ArticleStatus.SCRAPED)
        assert len(scraped) == 1
        assert scraped[0].id == "a1"

    def test_update_status(self, service, sample_source):
        """Test updating article status."""
        article = Article(
            id="update_test",
            title="Update Test",
            url="https://example.com/update",
            source=sample_source,
        )
        service.save(article)

        service.update_status("update_test", ArticleStatus.RANKED)

        updated = service.get("update_test")
        assert updated.status == ArticleStatus.RANKED

    def test_delete(self, service, sample_source):
        """Test deleting an article."""
        article = Article(
            id="delete_test",
            title="Delete Test",
            url="https://example.com/delete",
            source=sample_source,
        )
        service.save(article)

        assert service.get("delete_test") is not None
        assert service.delete("delete_test")
        assert service.get("delete_test") is None

    def test_exists(self, service, sample_source):
        """Test checking if article exists."""
        url = "https://example.com/exists"
        assert not service.exists(url)

        article = Article(
            id=service.generate_id(url),
            title="Exists Test",
            url=url,
            source=sample_source,
        )
        service.save(article)

        assert service.exists(url)

    def test_count(self, service, sample_source):
        """Test counting articles."""
        assert service.count() == 0

        for i in range(5):
            article = Article(
                id=f"count{i}",
                title=f"Count {i}",
                url=f"https://example.com/count/{i}",
                source=sample_source,
            )
            service.save(article)

        assert service.count() == 5

    def test_search(self, service, sample_source):
        """Test searching articles."""
        article1 = Article(
            id="search1",
            title="Python Programming Guide",
            url="https://example.com/python",
            source=sample_source,
            content="Learn Python basics",
        )
        article2 = Article(
            id="search2",
            title="JavaScript Tutorial",
            url="https://example.com/js",
            source=sample_source,
            content="JavaScript for beginners",
        )

        service.save(article1)
        service.save(article2)

        results = service.search("Python")
        assert len(results) == 1
        assert results[0].id == "search1"

    def test_get_categories(self, service, sample_source):
        """Test getting unique categories."""
        for cat in ["Tech", "Sports", "Tech"]:
            article = Article(
                id=f"cat_{cat}_{hash(cat)}",
                title=f"{cat} Article",
                url=f"https://example.com/{cat}/{hash(cat)}",
                source=sample_source,
                category=cat,
            )
            service.save(article)

        categories = service.get_categories()
        assert "Tech" in categories
        assert "Sports" in categories
        assert len(categories) == 2

    def test_bulk_save(self, service, sample_source):
        """Test bulk saving articles."""
        articles = [
            Article(
                id=f"bulk{i}",
                title=f"Bulk Article {i}",
                url=f"https://example.com/bulk/{i}",
                source=sample_source,
            )
            for i in range(10)
        ]

        saved = service.bulk_save(articles)
        assert saved == 10
        assert service.count() == 10

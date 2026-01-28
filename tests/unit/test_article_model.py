"""Tests for Article model."""

import pytest
from datetime import datetime
from app.models.article import Article, ArticleStatus, ArticleSource


class TestArticleSource:
    """Tests for ArticleSource dataclass."""

    def test_create_source(self):
        """Test creating an article source."""
        source = ArticleSource(
            name="Reuters",
            url="https://reuters.com",
            domain="reuters.com",
        )
        assert source.name == "Reuters"
        assert source.domain == "reuters.com"
        assert source.reliability_score == 0.5

    def test_source_to_dict(self):
        """Test converting source to dictionary."""
        source = ArticleSource(
            name="BBC",
            url="https://bbc.com",
            domain="bbc.com",
            reliability_score=0.9,
            category="News",
        )
        data = source.to_dict()
        assert data['name'] == "BBC"
        assert data['reliability_score'] == 0.9
        assert data['category'] == "News"

    def test_source_from_dict(self):
        """Test creating source from dictionary."""
        data = {
            'name': 'CNN',
            'url': 'https://cnn.com',
            'domain': 'cnn.com',
            'reliability_score': 0.75,
        }
        source = ArticleSource.from_dict(data)
        assert source.name == 'CNN'
        assert source.reliability_score == 0.75


class TestArticle:
    """Tests for Article dataclass."""

    @pytest.fixture
    def sample_source(self):
        """Create a sample source for testing."""
        return ArticleSource(
            name="Test Source",
            url="https://test.com",
            domain="test.com",
        )

    @pytest.fixture
    def sample_article(self, sample_source):
        """Create a sample article for testing."""
        return Article(
            id="test123",
            title="Test Article Title",
            url="https://test.com/article",
            source=sample_source,
            content="This is test content that is long enough to pass validation.",
        )

    def test_create_article(self, sample_source):
        """Test creating an article."""
        article = Article(
            id="abc123",
            title="Breaking News",
            url="https://example.com/news",
            source=sample_source,
        )
        assert article.id == "abc123"
        assert article.title == "Breaking News"
        assert article.status == ArticleStatus.SCRAPED

    def test_article_is_valid(self, sample_article):
        """Test article validation."""
        assert sample_article.is_valid()

        # Article without title should be invalid
        invalid_article = Article(
            id="test",
            title="",
            url="https://example.com",
            source=sample_article.source,
        )
        assert not invalid_article.is_valid()

    def test_article_has_content(self, sample_article):
        """Test content length check."""
        assert sample_article.has_content()

        # Short content
        sample_article.content = "Too short"
        assert not sample_article.has_content()

    def test_article_has_image(self, sample_article):
        """Test image availability check."""
        assert not sample_article.has_image()

        sample_article.image_url = "https://example.com/image.jpg"
        assert sample_article.has_image()

    def test_article_to_dict(self, sample_article):
        """Test converting article to dictionary."""
        data = sample_article.to_dict()
        assert data['id'] == "test123"
        assert data['title'] == "Test Article Title"
        assert data['status'] == "scraped"
        assert 'source' in data

    def test_article_from_dict(self):
        """Test creating article from dictionary."""
        data = {
            'id': 'xyz789',
            'title': 'From Dict Article',
            'url': 'https://example.com/from-dict',
            'source': {
                'name': 'Dict Source',
                'url': 'https://source.com',
                'domain': 'source.com',
            },
            'content': 'Article content here',
            'status': 'ranked',
            'rank_score': 0.85,
        }
        article = Article.from_dict(data)
        assert article.id == 'xyz789'
        assert article.title == 'From Dict Article'
        assert article.status == ArticleStatus.RANKED
        assert article.rank_score == 0.85

    def test_article_status_values(self):
        """Test all article status values."""
        assert ArticleStatus.SCRAPED.value == "scraped"
        assert ArticleStatus.RANKED.value == "ranked"
        assert ArticleStatus.ENHANCED.value == "enhanced"
        assert ArticleStatus.PUBLISHED.value == "published"
        assert ArticleStatus.REJECTED.value == "rejected"
        assert ArticleStatus.ERROR.value == "error"

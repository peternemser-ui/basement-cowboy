"""Tests for SEOService."""

import pytest
from datetime import datetime

from app.services.seo_service import SEOService
from app.models.article import Article, ArticleSource


class TestSEOService:
    """Tests for SEOService."""

    @pytest.fixture
    def service(self):
        """Create SEO service."""
        return SEOService(
            site_name="Test Site",
            site_url="https://testsite.com",
        )

    @pytest.fixture
    def sample_article(self):
        """Create sample article."""
        return Article(
            id="test123",
            title="Breaking News: Major Technology Announcement Made Today",
            url="https://source.com/article",
            source=ArticleSource(
                name="Tech News",
                url="https://technews.com",
                domain="technews.com",
            ),
            content="This is a long article content. " * 50,
            excerpt="Short excerpt for the article.",
            author="John Doe",
            category="Technology",
            tags=["tech", "news", "breaking"],
            image_url="https://example.com/image.jpg",
            scraped_at=datetime.now(),
        )

    def test_generate_metadata(self, service, sample_article):
        """Test generating complete SEO metadata."""
        metadata = service.generate_metadata(sample_article)

        assert metadata.title
        assert metadata.description
        assert metadata.keywords
        assert metadata.open_graph
        assert metadata.twitter_card
        assert metadata.schema_markup

    def test_optimize_title(self, service):
        """Test title optimization."""
        # Short title should stay as is
        short = "Short Title"
        assert service._optimize_title(short) == short

        # Long title should be truncated
        long_title = "A" * 100
        optimized = service._optimize_title(long_title)
        assert len(optimized) <= 60
        assert optimized.endswith("...")

    def test_generate_description(self, service, sample_article):
        """Test description generation."""
        description = service._generate_description(sample_article)

        assert len(description) <= 160
        assert description  # Not empty

    def test_extract_keywords(self, service, sample_article):
        """Test keyword extraction."""
        keywords = service._extract_keywords(sample_article)

        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        # Should include tags
        assert any(k in ['tech', 'news', 'breaking', 'Technology'] for k in keywords)

    def test_generate_slug(self, service):
        """Test slug generation."""
        slug = service._generate_slug("This Is A Test Title!")
        assert slug == "this-is-a-test-title"
        assert len(slug) <= 50

    def test_open_graph_generation(self, service, sample_article):
        """Test Open Graph data generation."""
        metadata = service.generate_metadata(sample_article)
        og = metadata.open_graph

        assert og.title
        assert og.description
        assert og.type == "article"
        assert og.site_name == "Test Site"
        assert og.image == sample_article.image_url

    def test_twitter_card_generation(self, service, sample_article):
        """Test Twitter Card data generation."""
        metadata = service.generate_metadata(sample_article)
        twitter = metadata.twitter_card

        assert twitter.title
        assert twitter.description
        assert twitter.card_type == "summary_large_image"
        assert twitter.image == sample_article.image_url

    def test_schema_markup_generation(self, service, sample_article):
        """Test Schema.org markup generation."""
        metadata = service.generate_metadata(sample_article)
        schema = metadata.schema_markup

        assert schema.type == "NewsArticle"
        assert schema.headline
        assert schema.author_name == "John Doe"
        assert schema.publisher_name == "Test Site"

    def test_json_ld_output(self, service, sample_article):
        """Test JSON-LD output."""
        metadata = service.generate_metadata(sample_article)
        json_ld = metadata.schema_markup.to_json_ld()

        assert json_ld["@context"] == "https://schema.org"
        assert json_ld["@type"] == "NewsArticle"
        assert "headline" in json_ld

    def test_meta_tags_generation(self, service, sample_article):
        """Test HTML meta tags generation."""
        tags = service.generate_meta_tags_html(sample_article)

        assert "<title>" in tags
        assert 'name="description"' in tags
        assert 'og:title' in tags

    def test_seo_score_analysis(self, service, sample_article):
        """Test SEO score analysis."""
        analysis = service.analyze_seo_score(sample_article)

        assert 'score' in analysis
        assert 'grade' in analysis
        assert 'issues' in analysis
        assert 'recommendations' in analysis
        assert analysis['score'] >= 0
        assert analysis['grade'] in ['A', 'B', 'C', 'D', 'F']

    def test_seo_score_no_image(self, service, sample_article):
        """Test SEO score without image."""
        sample_article.image_url = None
        sample_article.generated_image_url = None

        analysis = service.analyze_seo_score(sample_article)

        # Should have recommendation about image
        assert any("image" in r.lower() for r in analysis['recommendations'])

    def test_seo_score_short_content(self, service, sample_article):
        """Test SEO score with short content."""
        sample_article.content = "Too short"

        analysis = service.analyze_seo_score(sample_article)

        assert any("content" in issue.lower() for issue in analysis['issues'])

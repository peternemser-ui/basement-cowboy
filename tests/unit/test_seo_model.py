"""Tests for SEO models."""

import pytest
from datetime import datetime
from app.models.seo import SEOMetadata, OpenGraphData, TwitterCardData, SchemaMarkup


class TestOpenGraphData:
    """Tests for OpenGraphData dataclass."""

    def test_create_og_data(self):
        """Test creating Open Graph data."""
        og = OpenGraphData(
            title="Test Article",
            description="This is a test description",
            image="https://example.com/image.jpg",
        )
        assert og.title == "Test Article"
        assert og.type == "article"
        assert og.site_name == "Basement Cowboy"

    def test_og_to_dict(self):
        """Test converting OG data to dictionary."""
        og = OpenGraphData(
            title="Test",
            description="Description",
            url="https://example.com/article",
        )
        data = og.to_dict()
        assert data['og:title'] == "Test"
        assert data['og:description'] == "Description"
        assert data['og:type'] == "article"

    def test_og_to_meta_tags(self):
        """Test generating meta tags."""
        og = OpenGraphData(
            title="Article Title",
            description="Article description",
        )
        tags = og.to_meta_tags()
        assert any('og:title' in tag for tag in tags)
        assert any('og:description' in tag for tag in tags)


class TestTwitterCardData:
    """Tests for TwitterCardData dataclass."""

    def test_create_twitter_card(self):
        """Test creating Twitter Card data."""
        twitter = TwitterCardData(
            title="Test Article",
            description="Test description",
            image="https://example.com/image.jpg",
        )
        assert twitter.title == "Test Article"
        assert twitter.card_type == "summary_large_image"

    def test_twitter_to_dict(self):
        """Test converting Twitter Card to dictionary."""
        twitter = TwitterCardData(
            title="Test",
            description="Description",
            site="@testsite",
        )
        data = twitter.to_dict()
        assert data['twitter:card'] == "summary_large_image"
        assert data['twitter:title'] == "Test"
        assert data['twitter:site'] == "@testsite"


class TestSchemaMarkup:
    """Tests for SchemaMarkup dataclass."""

    def test_create_schema(self):
        """Test creating Schema.org markup."""
        schema = SchemaMarkup(
            headline="Test Headline",
            description="Test description",
            author_name="John Doe",
        )
        assert schema.type == "NewsArticle"
        assert schema.headline == "Test Headline"
        assert schema.publisher_name == "Basement Cowboy"

    def test_schema_to_json_ld(self):
        """Test generating JSON-LD."""
        schema = SchemaMarkup(
            headline="News Headline",
            description="News description",
            author_name="Jane Smith",
            date_published=datetime(2024, 1, 15, 12, 0, 0),
        )
        json_ld = schema.to_json_ld()
        assert json_ld['@context'] == "https://schema.org"
        assert json_ld['@type'] == "NewsArticle"
        assert json_ld['headline'] == "News Headline"
        assert 'author' in json_ld
        assert json_ld['author']['name'] == "Jane Smith"

    def test_schema_to_script_tag(self):
        """Test generating script tag."""
        schema = SchemaMarkup(
            headline="Test",
            description="Description",
        )
        script = schema.to_script_tag()
        assert '<script type="application/ld+json">' in script
        assert '"@context"' in script
        assert '</script>' in script


class TestSEOMetadata:
    """Tests for SEOMetadata dataclass."""

    def test_create_seo_metadata(self):
        """Test creating SEO metadata."""
        seo = SEOMetadata(
            title="Page Title",
            description="Page description for search engines",
            keywords=["news", "article", "breaking"],
        )
        assert seo.title == "Page Title"
        assert seo.robots == "index, follow"
        assert len(seo.keywords) == 3

    def test_seo_to_dict(self):
        """Test converting SEO metadata to dictionary."""
        og = OpenGraphData(title="Test", description="Desc")
        seo = SEOMetadata(
            title="Test Title",
            description="Test description",
            open_graph=og,
        )
        data = seo.to_dict()
        assert data['title'] == "Test Title"
        assert data['open_graph'] is not None

    def test_generate_meta_tags(self):
        """Test generating all meta tags."""
        seo = SEOMetadata(
            title="Full Test",
            description="Full description",
            keywords=["test", "seo"],
            canonical_url="https://example.com/canonical",
            author="Test Author",
        )
        tags = seo.generate_meta_tags()
        assert any('<title>' in tag for tag in tags)
        assert any('description' in tag for tag in tags)
        assert any('canonical' in tag for tag in tags)
        assert any('author' in tag for tag in tags)

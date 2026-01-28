"""Tests for WordPress models."""

import pytest
from datetime import datetime
from app.models.wordpress import (
    WordPressPost, WordPressMedia, PublishResult,
    PostStatus, MediaType
)


class TestPostStatus:
    """Tests for PostStatus enum."""

    def test_status_values(self):
        """Test post status values."""
        assert PostStatus.DRAFT.value == "draft"
        assert PostStatus.PUBLISH.value == "publish"
        assert PostStatus.PENDING.value == "pending"
        assert PostStatus.PRIVATE.value == "private"


class TestMediaType:
    """Tests for MediaType enum."""

    def test_media_type_values(self):
        """Test media type values."""
        assert MediaType.IMAGE.value == "image"
        assert MediaType.VIDEO.value == "video"
        assert MediaType.AUDIO.value == "audio"


class TestWordPressMedia:
    """Tests for WordPressMedia dataclass."""

    def test_create_media(self):
        """Test creating media object."""
        media = WordPressMedia(
            id=123,
            url="https://example.com/wp-content/uploads/image.jpg",
            title="Featured Image",
            alt_text="Article featured image",
        )
        assert media.id == 123
        assert media.media_type == MediaType.IMAGE

    def test_media_to_dict(self):
        """Test converting media to dictionary."""
        media = WordPressMedia(
            id=456,
            url="https://example.com/image.png",
            title="Test Image",
            width=1200,
            height=800,
        )
        data = media.to_dict()
        assert data['id'] == 456
        assert data['width'] == 1200
        assert data['height'] == 800

    def test_media_from_dict(self):
        """Test creating media from dictionary."""
        data = {
            'id': 789,
            'url': 'https://example.com/photo.jpg',
            'title': 'Photo',
            'media_type': 'image',
        }
        media = WordPressMedia.from_dict(data)
        assert media.id == 789
        assert media.media_type == MediaType.IMAGE


class TestWordPressPost:
    """Tests for WordPressPost dataclass."""

    def test_create_post(self):
        """Test creating a post."""
        post = WordPressPost(
            title="Test Post Title",
            content="<p>Post content here</p>",
            excerpt="Short excerpt",
        )
        assert post.title == "Test Post Title"
        assert post.status == PostStatus.DRAFT

    def test_post_to_api_payload(self):
        """Test converting post to API payload."""
        post = WordPressPost(
            title="API Test Post",
            content="Content for API",
            excerpt="Excerpt",
            status=PostStatus.PUBLISH,
            categories=[1, 2],
            tags=[5, 6, 7],
        )
        payload = post.to_api_payload()
        assert payload['title'] == "API Test Post"
        assert payload['status'] == "publish"
        assert payload['categories'] == [1, 2]
        assert payload['tags'] == [5, 6, 7]

    def test_post_with_featured_media(self):
        """Test post with featured media."""
        post = WordPressPost(
            title="Post with Image",
            content="Content",
            featured_media=123,
        )
        payload = post.to_api_payload()
        assert payload['featured_media'] == 123

    def test_post_with_meta_fields(self):
        """Test post with SEO meta fields."""
        post = WordPressPost(
            title="SEO Post",
            content="Content",
            meta_title="Custom Meta Title",
            meta_description="Custom meta description",
            focus_keyword="seo keyword",
        )
        payload = post.to_api_payload()
        assert 'meta' in payload
        assert payload['meta']['_yoast_wpseo_title'] == "Custom Meta Title"

    def test_post_to_graphql_input(self):
        """Test converting post to GraphQL input."""
        post = WordPressPost(
            title="GraphQL Post",
            content="Content",
            status=PostStatus.DRAFT,
            slug="graphql-post",
        )
        input_data = post.to_graphql_input()
        assert input_data['title'] == "GraphQL Post"
        assert input_data['status'] == "DRAFT"
        assert input_data['slug'] == "graphql-post"


class TestPublishResult:
    """Tests for PublishResult dataclass."""

    def test_success_result(self):
        """Test creating success result."""
        result = PublishResult.success(
            post_id=123,
            post_url="https://example.com/post/123"
        )
        assert result.success is True
        assert result.post_id == 123
        assert result.post_url == "https://example.com/post/123"

    def test_error_result(self):
        """Test creating error result."""
        result = PublishResult.error("Connection failed")
        assert result.success is False
        assert result.error_message == "Connection failed"
        assert result.post_id is None

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = PublishResult(
            success=True,
            post_id=456,
            post_url="https://example.com/post/456",
            media_id=789,
            publish_time_ms=150.5,
        )
        data = result.to_dict()
        assert data['success'] is True
        assert data['post_id'] == 456
        assert data['media_id'] == 789
        assert data['publish_time_ms'] == 150.5

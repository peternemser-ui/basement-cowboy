"""WordPress data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class PostStatus(Enum):
    """WordPress post status."""
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISH = "publish"
    FUTURE = "future"
    PRIVATE = "private"
    TRASH = "trash"


class MediaType(Enum):
    """WordPress media type."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    APPLICATION = "application"


@dataclass
class WordPressMedia:
    """WordPress media attachment."""
    id: Optional[int] = None
    url: str = ""
    title: str = ""
    alt_text: str = ""
    caption: str = ""
    description: str = ""
    media_type: MediaType = MediaType.IMAGE
    mime_type: str = "image/jpeg"
    width: int = 0
    height: int = 0
    file_size: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'alt_text': self.alt_text,
            'caption': self.caption,
            'description': self.description,
            'media_type': self.media_type.value,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WordPressMedia':
        media_type = data.get('media_type', 'image')
        if isinstance(media_type, str):
            try:
                media_type = MediaType(media_type)
            except ValueError:
                media_type = MediaType.IMAGE

        return cls(
            id=data.get('id'),
            url=data.get('url', ''),
            title=data.get('title', ''),
            alt_text=data.get('alt_text', ''),
            caption=data.get('caption', ''),
            description=data.get('description', ''),
            media_type=media_type,
            mime_type=data.get('mime_type', 'image/jpeg'),
            width=data.get('width', 0),
            height=data.get('height', 0),
            file_size=data.get('file_size', 0),
        )


@dataclass
class WordPressPost:
    """WordPress post data."""
    title: str
    content: str
    excerpt: str = ""
    status: PostStatus = PostStatus.DRAFT

    # IDs
    id: Optional[int] = None
    slug: Optional[str] = None

    # Taxonomies
    categories: List[int] = field(default_factory=list)
    tags: List[int] = field(default_factory=list)

    # Featured image
    featured_media: Optional[int] = None
    featured_image: Optional[WordPressMedia] = None

    # Dates
    date: Optional[datetime] = None
    modified: Optional[datetime] = None

    # Author
    author: Optional[int] = None

    # SEO
    meta_title: str = ""
    meta_description: str = ""
    focus_keyword: str = ""

    # Custom fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    # Source tracking
    source_url: Optional[str] = None
    source_name: Optional[str] = None

    def to_api_payload(self) -> Dict[str, Any]:
        """Convert to WordPress REST API payload."""
        payload = {
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'status': self.status.value,
        }

        if self.slug:
            payload['slug'] = self.slug

        if self.categories:
            payload['categories'] = self.categories

        if self.tags:
            payload['tags'] = self.tags

        if self.featured_media:
            payload['featured_media'] = self.featured_media

        if self.date:
            payload['date'] = self.date.isoformat()

        if self.author:
            payload['author'] = self.author

        # Add meta fields
        meta = {}
        if self.meta_title:
            meta['_yoast_wpseo_title'] = self.meta_title
        if self.meta_description:
            meta['_yoast_wpseo_metadesc'] = self.meta_description
        if self.focus_keyword:
            meta['_yoast_wpseo_focuskw'] = self.focus_keyword
        if self.source_url:
            meta['_source_url'] = self.source_url
        if self.source_name:
            meta['_source_name'] = self.source_name

        meta.update(self.custom_fields)

        if meta:
            payload['meta'] = meta

        return payload

    def to_graphql_input(self) -> Dict[str, Any]:
        """Convert to WPGraphQL mutation input."""
        return {
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'status': self.status.value.upper(),
            'slug': self.slug,
            'categoryIds': self.categories,
            'tagIds': self.tags,
        }


@dataclass
class PublishResult:
    """Result of publishing to WordPress."""
    success: bool
    post_id: Optional[int] = None
    post_url: Optional[str] = None
    error_message: Optional[str] = None
    media_id: Optional[int] = None
    media_url: Optional[str] = None

    # Timing
    publish_time_ms: float = 0.0
    media_upload_time_ms: float = 0.0

    # Costs
    ai_cost: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'post_id': self.post_id,
            'post_url': self.post_url,
            'error_message': self.error_message,
            'media_id': self.media_id,
            'media_url': self.media_url,
            'publish_time_ms': self.publish_time_ms,
            'media_upload_time_ms': self.media_upload_time_ms,
            'ai_cost': self.ai_cost,
        }

    @classmethod
    def error(cls, message: str) -> 'PublishResult':
        """Create an error result."""
        return cls(success=False, error_message=message)

    @classmethod
    def success(cls, post_id: int, post_url: str) -> 'PublishResult':
        """Create a success result."""
        return cls(success=True, post_id=post_id, post_url=post_url)

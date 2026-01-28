"""WordPress integration service."""

import os
import base64
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urljoin

from app.models.wordpress import WordPressPost, WordPressMedia, PublishResult, PostStatus
from app.models.config import WordPressConfig


class WordPressService:
    """Service for WordPress API integration."""

    def __init__(self, config: Optional[WordPressConfig] = None):
        self.config = config or WordPressConfig.from_env()
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """Get or create authenticated session."""
        if self._session is None:
            self._session = requests.Session()
            # Set basic auth
            credentials = f"{self.config.username}:{self.config.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self._session.headers.update({
                'Authorization': f'Basic {encoded}',
                'Content-Type': 'application/json',
            })
        return self._session

    def is_configured(self) -> bool:
        """Check if WordPress is configured."""
        return self.config.is_configured()

    def _rest_url(self, endpoint: str) -> str:
        """Build REST API URL."""
        base = urljoin(self.config.site_url, self.config.rest_endpoint)
        return urljoin(base + '/', endpoint)

    def _graphql_url(self) -> str:
        """Build GraphQL URL."""
        return urljoin(self.config.site_url, self.config.graphql_endpoint)

    def test_connection(self) -> Dict[str, Any]:
        """Test WordPress connection."""
        try:
            response = self.session.get(self._rest_url(''))
            response.raise_for_status()
            return {
                'success': True,
                'message': 'Connection successful',
                'site_info': response.json() if response.text else {},
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': str(e),
                'site_info': {},
            }

    def create_post(self, post: WordPressPost) -> PublishResult:
        """Create a new WordPress post."""
        start_time = datetime.now()

        try:
            payload = post.to_api_payload()
            response = self.session.post(
                self._rest_url('posts'),
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            elapsed = (datetime.now() - start_time).total_seconds() * 1000

            return PublishResult(
                success=True,
                post_id=data.get('id'),
                post_url=data.get('link'),
                publish_time_ms=elapsed,
            )
        except requests.exceptions.RequestException as e:
            return PublishResult.error(str(e))

    def update_post(self, post_id: int, post: WordPressPost) -> PublishResult:
        """Update an existing WordPress post."""
        try:
            payload = post.to_api_payload()
            response = self.session.post(
                self._rest_url(f'posts/{post_id}'),
                json=payload,
            )
            response.raise_for_status()

            data = response.json()
            return PublishResult(
                success=True,
                post_id=data.get('id'),
                post_url=data.get('link'),
            )
        except requests.exceptions.RequestException as e:
            return PublishResult.error(str(e))

    def delete_post(self, post_id: int, force: bool = False) -> bool:
        """Delete a WordPress post."""
        try:
            params = {'force': force}
            response = self.session.delete(
                self._rest_url(f'posts/{post_id}'),
                params=params,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get a WordPress post by ID."""
        try:
            response = self.session.get(self._rest_url(f'posts/{post_id}'))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def get_posts(
        self,
        status: str = 'publish',
        per_page: int = 10,
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get WordPress posts."""
        try:
            params = {
                'status': status,
                'per_page': per_page,
                'page': page,
            }
            response = self.session.get(self._rest_url('posts'), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def upload_media(
        self,
        file_path: Optional[str] = None,
        file_url: Optional[str] = None,
        title: str = "",
        alt_text: str = "",
    ) -> Optional[WordPressMedia]:
        """Upload media to WordPress."""
        start_time = datetime.now()

        try:
            if file_url:
                # Download image from URL
                img_response = requests.get(file_url, timeout=30)
                img_response.raise_for_status()
                file_data = img_response.content
                content_type = img_response.headers.get('Content-Type', 'image/jpeg')
                filename = file_url.split('/')[-1].split('?')[0] or 'image.jpg'
            elif file_path:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                content_type = 'image/jpeg'  # Simplified
                filename = os.path.basename(file_path)
            else:
                return None

            # Upload to WordPress
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': content_type,
            }

            # Use a clean session for file upload
            upload_session = requests.Session()
            credentials = f"{self.config.username}:{self.config.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            upload_session.headers.update({'Authorization': f'Basic {encoded}'})

            response = upload_session.post(
                self._rest_url('media'),
                data=file_data,
                headers=headers,
            )
            response.raise_for_status()

            data = response.json()
            elapsed = (datetime.now() - start_time).total_seconds() * 1000

            return WordPressMedia(
                id=data.get('id'),
                url=data.get('source_url', ''),
                title=data.get('title', {}).get('rendered', title),
                alt_text=alt_text,
            )
        except Exception as e:
            print(f"Media upload failed: {e}")
            return None

    def set_featured_image(self, post_id: int, media_id: int) -> bool:
        """Set featured image for a post."""
        try:
            response = self.session.post(
                self._rest_url(f'posts/{post_id}'),
                json={'featured_media': media_id},
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all WordPress categories."""
        try:
            response = self.session.get(
                self._rest_url('categories'),
                params={'per_page': 100},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all WordPress tags."""
        try:
            response = self.session.get(
                self._rest_url('tags'),
                params={'per_page': 100},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return []

    def create_tag(self, name: str) -> Optional[int]:
        """Create a tag and return its ID."""
        try:
            response = self.session.post(
                self._rest_url('tags'),
                json={'name': name},
            )
            response.raise_for_status()
            return response.json().get('id')
        except requests.exceptions.RequestException:
            return None

    def get_or_create_tag(self, name: str) -> Optional[int]:
        """Get existing tag ID or create new one."""
        tags = self.get_tags()
        for tag in tags:
            if tag.get('name', '').lower() == name.lower():
                return tag.get('id')
        return self.create_tag(name)

    def publish_article(
        self,
        title: str,
        content: str,
        excerpt: str = "",
        image_url: Optional[str] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        status: str = "draft",
        source_url: Optional[str] = None,
    ) -> PublishResult:
        """High-level method to publish an article with all metadata."""
        # Upload featured image if provided
        media_id = None
        media_url = None
        if image_url:
            media = self.upload_media(file_url=image_url, title=title, alt_text=title)
            if media:
                media_id = media.id
                media_url = media.url

        # Get or create tags
        tag_ids = []
        if tags:
            for tag_name in tags:
                tag_id = self.get_or_create_tag(tag_name)
                if tag_id:
                    tag_ids.append(tag_id)

        # Create post
        post = WordPressPost(
            title=title,
            content=content,
            excerpt=excerpt,
            status=PostStatus(status),
            featured_media=media_id,
            categories=[category_id] if category_id else [],
            tags=tag_ids,
            source_url=source_url,
        )

        result = self.create_post(post)
        result.media_id = media_id
        result.media_url = media_url

        return result

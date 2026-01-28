"""Article management service."""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.models.article import Article, ArticleStatus, ArticleSource


class ArticleService:
    """Service for managing articles."""

    def __init__(self, storage_path: str = "output/news_articles"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Article] = {}

    def generate_id(self, url: str) -> str:
        """Generate a unique ID for an article based on its URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def create(
        self,
        title: str,
        url: str,
        source_name: str,
        source_url: str,
        content: str = "",
        **kwargs
    ) -> Article:
        """Create a new article."""
        article_id = self.generate_id(url)

        source = ArticleSource(
            name=source_name,
            url=source_url,
            domain=self._extract_domain(source_url),
            reliability_score=kwargs.get('reliability_score', 0.5),
            category=kwargs.get('source_category'),
            country=kwargs.get('source_country'),
        )

        article = Article(
            id=article_id,
            title=title,
            url=url,
            source=source,
            content=content,
            summary=kwargs.get('summary', ''),
            excerpt=kwargs.get('excerpt', ''),
            image_url=kwargs.get('image_url'),
            images=kwargs.get('images', []),
            author=kwargs.get('author'),
            category=kwargs.get('category'),
            tags=kwargs.get('tags', []),
        )

        return article

    def save(self, article: Article) -> bool:
        """Save an article to storage."""
        try:
            file_path = self._get_file_path(article.id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article.to_dict(), f, indent=2, ensure_ascii=False)
            self._cache[article.id] = article
            return True
        except Exception as e:
            print(f"Error saving article {article.id}: {e}")
            return False

    def get(self, article_id: str) -> Optional[Article]:
        """Get an article by ID."""
        if article_id in self._cache:
            return self._cache[article_id]

        file_path = self._get_file_path(article_id)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                article = Article.from_dict(data)
                self._cache[article_id] = article
                return article
            except Exception as e:
                print(f"Error loading article {article_id}: {e}")
        return None

    def get_all(self, status: Optional[ArticleStatus] = None) -> List[Article]:
        """Get all articles, optionally filtered by status."""
        articles = []
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                article = Article.from_dict(data)
                if status is None or article.status == status:
                    articles.append(article)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        return sorted(articles, key=lambda a: a.scraped_at, reverse=True)

    def get_recent(self, limit: int = 50) -> List[Article]:
        """Get most recent articles."""
        articles = self.get_all()
        return articles[:limit]

    def get_by_category(self, category: str) -> List[Article]:
        """Get articles by category."""
        return [a for a in self.get_all() if a.category == category]

    def get_by_source(self, source_name: str) -> List[Article]:
        """Get articles by source."""
        return [a for a in self.get_all() if a.source.name == source_name]

    def update(self, article: Article) -> bool:
        """Update an existing article."""
        return self.save(article)

    def update_status(self, article_id: str, status: ArticleStatus) -> bool:
        """Update article status."""
        article = self.get(article_id)
        if article:
            article.status = status
            return self.save(article)
        return False

    def delete(self, article_id: str) -> bool:
        """Delete an article."""
        file_path = self._get_file_path(article_id)
        try:
            if file_path.exists():
                file_path.unlink()
            if article_id in self._cache:
                del self._cache[article_id]
            return True
        except Exception as e:
            print(f"Error deleting article {article_id}: {e}")
            return False

    def exists(self, url: str) -> bool:
        """Check if an article with the given URL already exists."""
        article_id = self.generate_id(url)
        return self._get_file_path(article_id).exists()

    def count(self, status: Optional[ArticleStatus] = None) -> int:
        """Count articles, optionally by status."""
        if status is None:
            return len(list(self.storage_path.glob("*.json")))
        return len(self.get_all(status=status))

    def search(self, query: str, limit: int = 20) -> List[Article]:
        """Search articles by title or content."""
        query_lower = query.lower()
        results = []
        for article in self.get_all():
            if (query_lower in article.title.lower() or
                query_lower in article.content.lower()):
                results.append(article)
                if len(results) >= limit:
                    break
        return results

    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        categories = set()
        for article in self.get_all():
            if article.category:
                categories.add(article.category)
        return sorted(list(categories))

    def get_sources(self) -> List[str]:
        """Get all unique sources."""
        sources = set()
        for article in self.get_all():
            sources.add(article.source.name)
        return sorted(list(sources))

    def cleanup_old(self, days: int = 7) -> int:
        """Remove articles older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        removed = 0
        for article in self.get_all():
            if article.scraped_at.timestamp() < cutoff:
                if self.delete(article.id):
                    removed += 1
        return removed

    def _get_file_path(self, article_id: str) -> Path:
        """Get the file path for an article."""
        return self.storage_path / f"{article_id}.json"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()

    def bulk_save(self, articles: List[Article]) -> int:
        """Save multiple articles, returns count of successful saves."""
        saved = 0
        for article in articles:
            if self.save(article):
                saved += 1
        return saved

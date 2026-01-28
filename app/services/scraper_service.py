"""Scraper orchestration service."""

import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from dataclasses import dataclass

from app.models.article import Article, ArticleSource, ArticleStatus
from app.models.config import ScraperConfig


@dataclass
class ScrapeResult:
    """Result of a scraping operation."""
    success: bool
    articles_found: int
    articles_saved: int
    errors: List[str]
    duration_seconds: float
    sources_scraped: int


class ScraperService:
    """Service for orchestrating news scraping."""

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.sources: List[str] = []
        self._load_sources()

    def _load_sources(self) -> None:
        """Load news sources from configuration file."""
        sources_path = Path(self.config.sources_file)
        if sources_path.exists():
            with open(sources_path, 'r') as f:
                self.sources = [
                    line.strip() for line in f
                    if line.strip() and not line.startswith('#')
                ]

    def get_sources(self) -> List[str]:
        """Get list of configured sources."""
        return self.sources.copy()

    def add_source(self, url: str) -> bool:
        """Add a new source URL."""
        if url not in self.sources:
            self.sources.append(url)
            self._save_sources()
            return True
        return False

    def remove_source(self, url: str) -> bool:
        """Remove a source URL."""
        if url in self.sources:
            self.sources.remove(url)
            self._save_sources()
            return True
        return False

    def _save_sources(self) -> None:
        """Save sources back to configuration file."""
        sources_path = Path(self.config.sources_file)
        with open(sources_path, 'w') as f:
            for source in self.sources:
                f.write(f"{source}\n")

    async def scrape_source(
        self,
        url: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> List[Article]:
        """Scrape articles from a single source."""
        articles = []

        try:
            if callback:
                callback(f"Scraping {url}...")

            # Import scraper modules
            from scraper.fetch_page import fetch_page
            from scraper.parse_articles import parse_articles

            # Fetch the page
            html = await self._fetch_with_retry(url)
            if not html:
                return articles

            # Parse articles
            raw_articles = parse_articles(html, url)

            # Convert to Article objects
            for raw in raw_articles[:self.config.max_articles_per_source]:
                article = self._convert_raw_article(raw, url)
                if article and article.is_valid():
                    articles.append(article)

        except Exception as e:
            if callback:
                callback(f"Error scraping {url}: {str(e)}")

        return articles

    async def _fetch_with_retry(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch URL with retry logic."""
        for attempt in range(retries):
            try:
                if self.config.use_playwright:
                    return await self._fetch_with_playwright(url)
                else:
                    return await self._fetch_with_requests(url)
            except Exception as e:
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))
        return None

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch URL using Playwright for JavaScript rendering."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.config.headless)
                page = await browser.new_page()
                page.set_default_timeout(self.config.timeout * 1000)

                await page.goto(url, wait_until='domcontentloaded')
                await page.wait_for_timeout(2000)  # Wait for dynamic content

                content = await page.content()
                await browser.close()

                return content
        except ImportError:
            # Fall back to requests if Playwright not available
            return await self._fetch_with_requests(url)

    async def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch URL using requests library."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': self.config.user_agent}
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            ) as response:
                if response.status == 200:
                    return await response.text()
        return None

    def _convert_raw_article(self, raw: Dict[str, Any], source_url: str) -> Optional[Article]:
        """Convert raw scraped data to Article object."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(source_url).netloc

            source = ArticleSource(
                name=raw.get('source_name', domain),
                url=source_url,
                domain=domain,
            )

            return Article(
                id=self._generate_id(raw.get('url', '')),
                title=raw.get('title', ''),
                url=raw.get('url', ''),
                source=source,
                content=raw.get('content', ''),
                excerpt=raw.get('excerpt', ''),
                image_url=raw.get('image_url'),
                images=raw.get('images', []),
                author=raw.get('author'),
                category=raw.get('category'),
                status=ArticleStatus.SCRAPED,
            )
        except Exception:
            return None

    def _generate_id(self, url: str) -> str:
        """Generate unique ID for article."""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]

    async def scrape_all(
        self,
        sources: Optional[List[str]] = None,
        max_articles: Optional[int] = None,
        callback: Optional[Callable[[str], None]] = None,
    ) -> ScrapeResult:
        """Scrape all configured sources."""
        start_time = datetime.now()
        sources = sources or self.sources
        max_articles = max_articles or self.config.max_total_articles

        all_articles: List[Article] = []
        errors: List[str] = []

        for source in sources:
            if len(all_articles) >= max_articles:
                break

            try:
                articles = await self.scrape_source(source, callback)
                remaining = max_articles - len(all_articles)
                all_articles.extend(articles[:remaining])

                # Rate limiting
                await asyncio.sleep(self.config.request_delay)

            except Exception as e:
                errors.append(f"{source}: {str(e)}")

        # Save articles
        saved = self._save_articles(all_articles)

        duration = (datetime.now() - start_time).total_seconds()

        return ScrapeResult(
            success=len(errors) == 0,
            articles_found=len(all_articles),
            articles_saved=saved,
            errors=errors,
            duration_seconds=duration,
            sources_scraped=len(sources),
        )

    def _save_articles(self, articles: List[Article]) -> int:
        """Save articles to storage."""
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved = 0
        for article in articles:
            try:
                file_path = output_path / f"{article.id}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(article.to_dict(), f, indent=2, ensure_ascii=False)
                saved += 1
            except Exception:
                pass

        return saved

    def filter_articles(
        self,
        articles: List[Article],
        min_content_length: Optional[int] = None,
        required_keywords: Optional[List[str]] = None,
        blocked_keywords: Optional[List[str]] = None,
    ) -> List[Article]:
        """Filter articles based on criteria."""
        min_length = min_content_length or self.config.min_content_length
        required = required_keywords or self.config.required_keywords
        blocked = blocked_keywords or self.config.blocked_keywords

        filtered = []
        for article in articles:
            # Length check
            if len(article.content) < min_length:
                continue

            # Required keywords check
            if required:
                content_lower = (article.title + ' ' + article.content).lower()
                if not any(kw.lower() in content_lower for kw in required):
                    continue

            # Blocked keywords check
            if blocked:
                content_lower = (article.title + ' ' + article.content).lower()
                if any(kw.lower() in content_lower for kw in blocked):
                    continue

            filtered.append(article)

        return filtered

    def deduplicate(self, articles: List[Article]) -> List[Article]:
        """Remove duplicate articles based on title similarity."""
        seen_titles: Dict[str, Article] = {}

        for article in articles:
            # Normalize title for comparison
            normalized = self._normalize_title(article.title)

            if normalized not in seen_titles:
                seen_titles[normalized] = article
            else:
                # Keep the one with more content
                existing = seen_titles[normalized]
                if len(article.content) > len(existing.content):
                    seen_titles[normalized] = article

        return list(seen_titles.values())

    def _normalize_title(self, title: str) -> str:
        """Normalize title for deduplication."""
        import re
        # Lowercase, remove punctuation, collapse whitespace
        normalized = title.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        return normalized

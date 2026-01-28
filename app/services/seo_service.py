"""SEO generation service."""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.article import Article
from app.models.seo import SEOMetadata, OpenGraphData, TwitterCardData, SchemaMarkup


class SEOService:
    """Service for generating SEO metadata."""

    MAX_TITLE_LENGTH = 60
    MAX_DESCRIPTION_LENGTH = 160

    def __init__(
        self,
        site_name: str = "Basement Cowboy",
        site_url: str = "",
        publisher_logo: Optional[str] = None,
    ):
        self.site_name = site_name
        self.site_url = site_url
        self.publisher_logo = publisher_logo

    def generate_metadata(self, article: Article) -> SEOMetadata:
        """Generate complete SEO metadata for an article."""
        # Generate title and description
        seo_title = self._optimize_title(article.title)
        description = self._generate_description(article)
        keywords = self._extract_keywords(article)
        canonical_url = self._generate_canonical(article)

        # Generate Open Graph data
        og_data = self._generate_open_graph(article, seo_title, description)

        # Generate Twitter Card data
        twitter_data = self._generate_twitter_card(article, seo_title, description)

        # Generate Schema.org markup
        schema = self._generate_schema_markup(article, seo_title, description)

        return SEOMetadata(
            title=seo_title,
            description=description,
            keywords=keywords,
            canonical_url=canonical_url,
            open_graph=og_data,
            twitter_card=twitter_data,
            schema_markup=schema,
            author=article.author,
        )

    def _optimize_title(self, title: str) -> str:
        """Optimize title for SEO."""
        # Remove excessive whitespace
        title = ' '.join(title.split())

        # Truncate if too long
        if len(title) > self.MAX_TITLE_LENGTH:
            # Try to cut at a word boundary
            truncated = title[:self.MAX_TITLE_LENGTH - 3]
            last_space = truncated.rfind(' ')
            if last_space > self.MAX_TITLE_LENGTH - 20:
                truncated = truncated[:last_space]
            title = truncated + '...'

        return title

    def _generate_description(self, article: Article) -> str:
        """Generate meta description."""
        # Use AI summary if available
        if article.ai_summary:
            text = article.ai_summary
        # Use excerpt if available
        elif article.excerpt:
            text = article.excerpt
        # Use summary
        elif article.summary:
            text = article.summary
        # Fall back to content beginning
        else:
            text = article.content

        # Clean and truncate
        text = ' '.join(text.split())
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags

        if len(text) > self.MAX_DESCRIPTION_LENGTH:
            truncated = text[:self.MAX_DESCRIPTION_LENGTH - 3]
            last_space = truncated.rfind(' ')
            if last_space > self.MAX_DESCRIPTION_LENGTH - 30:
                truncated = truncated[:last_space]
            text = truncated + '...'

        return text

    def _extract_keywords(self, article: Article) -> List[str]:
        """Extract keywords from article."""
        keywords = []

        # Use tags if available
        if article.tags:
            keywords.extend(article.tags[:5])

        # Add category
        if article.category:
            keywords.append(article.category)

        # Extract from title
        title_words = self._extract_significant_words(article.title)
        keywords.extend(title_words[:5])

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                seen.add(kw_lower)
                unique_keywords.append(kw)

        return unique_keywords[:10]

    def _extract_significant_words(self, text: str) -> List[str]:
        """Extract significant words from text."""
        # Common stop words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'this', 'that', 'these', 'those', 'it', 'its', "it's", 'they', 'them',
            'their', 'we', 'us', 'our', 'you', 'your', 'he', 'she', 'him', 'her',
            'his', 'hers', 'what', 'which', 'who', 'whom', 'when', 'where', 'why',
            'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'also', 'now', 'new', 'says', 'said',
        }

        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        significant = [w for w in words if w not in stop_words]

        return significant

    def _generate_canonical(self, article: Article) -> str:
        """Generate canonical URL."""
        if article.wordpress_url:
            return article.wordpress_url
        if self.site_url:
            slug = self._generate_slug(article.title)
            return f"{self.site_url.rstrip('/')}/{slug}"
        return article.url

    def _generate_slug(self, title: str) -> str:
        """Generate URL slug from title."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return slug[:50]  # Limit length

    def _generate_open_graph(
        self,
        article: Article,
        title: str,
        description: str,
    ) -> OpenGraphData:
        """Generate Open Graph metadata."""
        image = article.generated_image_url or article.image_url
        if article.images and not image:
            image = article.images[0]

        return OpenGraphData(
            title=title,
            description=description,
            image=image,
            url=self._generate_canonical(article),
            type="article",
            site_name=self.site_name,
        )

    def _generate_twitter_card(
        self,
        article: Article,
        title: str,
        description: str,
    ) -> TwitterCardData:
        """Generate Twitter Card metadata."""
        image = article.generated_image_url or article.image_url
        if article.images and not image:
            image = article.images[0]

        return TwitterCardData(
            title=title,
            description=description,
            image=image,
            card_type="summary_large_image" if image else "summary",
        )

    def _generate_schema_markup(
        self,
        article: Article,
        title: str,
        description: str,
    ) -> SchemaMarkup:
        """Generate Schema.org markup."""
        image = article.generated_image_url or article.image_url
        if article.images and not image:
            image = article.images[0]

        return SchemaMarkup(
            type="NewsArticle",
            headline=title,
            description=description,
            image=image,
            author_name=article.author,
            publisher_name=self.site_name,
            publisher_logo=self.publisher_logo,
            date_published=article.published_at or article.scraped_at,
            date_modified=datetime.now(),
            main_entity_url=self._generate_canonical(article),
            keywords=article.tags,
        )

    def generate_meta_tags_html(self, article: Article) -> str:
        """Generate complete HTML meta tags block."""
        metadata = self.generate_metadata(article)
        tags = metadata.generate_meta_tags()

        if metadata.schema_markup:
            tags.append(metadata.schema_markup.to_script_tag())

        return '\n'.join(tags)

    def analyze_seo_score(self, article: Article) -> Dict[str, Any]:
        """Analyze SEO quality and provide recommendations."""
        score = 100
        issues = []
        recommendations = []

        # Title checks
        title_len = len(article.title)
        if title_len < 30:
            score -= 10
            issues.append("Title is too short")
            recommendations.append("Aim for titles between 50-60 characters")
        elif title_len > 70:
            score -= 5
            issues.append("Title may be truncated in search results")
            recommendations.append("Keep titles under 60 characters")

        # Description/content checks
        content_len = len(article.content)
        if content_len < 300:
            score -= 15
            issues.append("Content is very short")
            recommendations.append("Add more substantive content (aim for 300+ words)")

        # Image checks
        if not article.image_url and not article.generated_image_url:
            score -= 10
            issues.append("No featured image")
            recommendations.append("Add a featured image for better social sharing")

        # Keywords in title
        if article.tags:
            title_lower = article.title.lower()
            has_keyword = any(tag.lower() in title_lower for tag in article.tags)
            if not has_keyword:
                score -= 5
                recommendations.append("Include primary keyword in the title")

        # Author attribution
        if not article.author:
            score -= 5
            recommendations.append("Add author attribution for credibility")

        return {
            'score': max(0, score),
            'grade': self._score_to_grade(score),
            'issues': issues,
            'recommendations': recommendations,
        }

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

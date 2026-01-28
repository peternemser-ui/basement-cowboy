"""SEO data models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class OpenGraphData:
    """Open Graph metadata for social sharing."""
    title: str
    description: str
    image: Optional[str] = None
    url: Optional[str] = None
    type: str = "article"
    site_name: str = "Basement Cowboy"
    locale: str = "en_US"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'og:title': self.title,
            'og:description': self.description,
            'og:image': self.image,
            'og:url': self.url,
            'og:type': self.type,
            'og:site_name': self.site_name,
            'og:locale': self.locale,
        }

    def to_meta_tags(self) -> List[str]:
        """Generate HTML meta tags."""
        tags = []
        for key, value in self.to_dict().items():
            if value:
                tags.append(f'<meta property="{key}" content="{value}" />')
        return tags


@dataclass
class TwitterCardData:
    """Twitter Card metadata."""
    title: str
    description: str
    image: Optional[str] = None
    card_type: str = "summary_large_image"
    site: Optional[str] = None
    creator: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'twitter:card': self.card_type,
            'twitter:title': self.title,
            'twitter:description': self.description,
            'twitter:image': self.image,
            'twitter:site': self.site,
            'twitter:creator': self.creator,
        }

    def to_meta_tags(self) -> List[str]:
        """Generate HTML meta tags."""
        tags = []
        for key, value in self.to_dict().items():
            if value:
                tags.append(f'<meta name="{key}" content="{value}" />')
        return tags


@dataclass
class SchemaMarkup:
    """Schema.org JSON-LD markup."""
    type: str = "NewsArticle"
    headline: str = ""
    description: str = ""
    image: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    publisher_name: str = "Basement Cowboy"
    publisher_logo: Optional[str] = None
    date_published: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    main_entity_url: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    def to_json_ld(self) -> Dict[str, Any]:
        """Generate JSON-LD structured data."""
        schema = {
            "@context": "https://schema.org",
            "@type": self.type,
            "headline": self.headline,
            "description": self.description,
        }

        if self.image:
            schema["image"] = self.image

        if self.author_name:
            schema["author"] = {
                "@type": "Person",
                "name": self.author_name,
            }
            if self.author_url:
                schema["author"]["url"] = self.author_url

        schema["publisher"] = {
            "@type": "Organization",
            "name": self.publisher_name,
        }
        if self.publisher_logo:
            schema["publisher"]["logo"] = {
                "@type": "ImageObject",
                "url": self.publisher_logo,
            }

        if self.date_published:
            schema["datePublished"] = self.date_published.isoformat()

        if self.date_modified:
            schema["dateModified"] = self.date_modified.isoformat()

        if self.main_entity_url:
            schema["mainEntityOfPage"] = {
                "@type": "WebPage",
                "@id": self.main_entity_url,
            }

        if self.keywords:
            schema["keywords"] = ", ".join(self.keywords)

        return schema

    def to_script_tag(self) -> str:
        """Generate HTML script tag with JSON-LD."""
        import json
        return f'<script type="application/ld+json">{json.dumps(self.to_json_ld(), indent=2)}</script>'


@dataclass
class SEOMetadata:
    """Complete SEO metadata for an article."""
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    robots: str = "index, follow"

    # Social metadata
    open_graph: Optional[OpenGraphData] = None
    twitter_card: Optional[TwitterCardData] = None

    # Structured data
    schema_markup: Optional[SchemaMarkup] = None

    # Additional meta
    author: Optional[str] = None
    language: str = "en"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'description': self.description,
            'keywords': self.keywords,
            'canonical_url': self.canonical_url,
            'robots': self.robots,
            'open_graph': self.open_graph.to_dict() if self.open_graph else None,
            'twitter_card': self.twitter_card.to_dict() if self.twitter_card else None,
            'schema_markup': self.schema_markup.to_json_ld() if self.schema_markup else None,
            'author': self.author,
            'language': self.language,
        }

    def generate_meta_tags(self) -> List[str]:
        """Generate all HTML meta tags."""
        tags = [
            f'<title>{self.title}</title>',
            f'<meta name="description" content="{self.description}" />',
            f'<meta name="robots" content="{self.robots}" />',
            f'<meta name="language" content="{self.language}" />',
        ]

        if self.keywords:
            tags.append(f'<meta name="keywords" content="{", ".join(self.keywords)}" />')

        if self.canonical_url:
            tags.append(f'<link rel="canonical" href="{self.canonical_url}" />')

        if self.author:
            tags.append(f'<meta name="author" content="{self.author}" />')

        if self.open_graph:
            tags.extend(self.open_graph.to_meta_tags())

        if self.twitter_card:
            tags.extend(self.twitter_card.to_meta_tags())

        return tags

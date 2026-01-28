"""Sample article fixtures for testing."""

from datetime import datetime, timedelta
from app.models.article import Article, ArticleSource, ArticleStatus


def create_sample_source(name: str = "Test Source") -> ArticleSource:
    """Create a sample article source."""
    domain = name.lower().replace(" ", "") + ".com"
    return ArticleSource(
        name=name,
        url=f"https://{domain}",
        domain=domain,
        reliability_score=0.75,
    )


def create_sample_article(
    id: str = "test123",
    title: str = "Sample Article Title",
    **kwargs
) -> Article:
    """Create a sample article with default values."""
    source = kwargs.pop('source', create_sample_source())

    defaults = {
        'id': id,
        'title': title,
        'url': f"https://example.com/{id}",
        'source': source,
        'content': "This is sample article content. " * 20,
        'excerpt': "This is the article excerpt.",
        'author': "Test Author",
        'category': "General",
        'tags': ["test", "sample"],
        'scraped_at': datetime.now(),
        'status': ArticleStatus.SCRAPED,
    }
    defaults.update(kwargs)

    return Article(**defaults)


def create_sample_articles(count: int = 5) -> list:
    """Create multiple sample articles."""
    sources = [
        ArticleSource(name="Reuters", url="https://reuters.com", domain="reuters.com", reliability_score=0.95),
        ArticleSource(name="BBC", url="https://bbc.com", domain="bbc.com", reliability_score=0.90),
        ArticleSource(name="CNN", url="https://cnn.com", domain="cnn.com", reliability_score=0.75),
        ArticleSource(name="TechCrunch", url="https://techcrunch.com", domain="techcrunch.com", reliability_score=0.70),
        ArticleSource(name="Local News", url="https://localnews.com", domain="localnews.com", reliability_score=0.50),
    ]

    categories = ["Politics", "Technology", "Sports", "Business", "Entertainment"]

    articles = []
    for i in range(count):
        source = sources[i % len(sources)]
        category = categories[i % len(categories)]

        article = Article(
            id=f"article_{i:03d}",
            title=f"Sample {category} Article {i+1}: Breaking News",
            url=f"https://{source.domain}/article/{i+1}",
            source=source,
            content=f"This is the content for article {i+1}. " * (50 + i * 10),
            excerpt=f"Excerpt for article {i+1}",
            author=f"Author {i+1}" if i % 2 == 0 else None,
            category=category,
            tags=[category.lower(), "news", "sample"],
            image_url=f"https://{source.domain}/images/{i+1}.jpg" if i % 3 != 0 else None,
            scraped_at=datetime.now() - timedelta(hours=i * 2),
            status=ArticleStatus.SCRAPED,
        )
        articles.append(article)

    return articles


def create_ranked_articles() -> list:
    """Create sample articles with ranking data."""
    articles = create_sample_articles(10)

    for i, article in enumerate(articles):
        article.status = ArticleStatus.RANKED
        article.rank_score = 1.0 - (i * 0.08)  # Decreasing scores
        article.ranking_details = {
            'quality': 0.8 - (i * 0.05),
            'credibility': 0.9 - (i * 0.03),
            'engagement': 0.7 - (i * 0.04),
            'visuals': 0.6 if article.image_url else 0.0,
            'timeliness': 1.0 - (i * 0.1),
        }

    return articles


def create_articles_for_category_test() -> list:
    """Create articles with various categories for testing."""
    source = create_sample_source()

    categories_data = [
        ("Politics", 3),
        ("Technology", 4),
        ("Sports", 2),
        ("Business", 3),
        ("Entertainment", 2),
    ]

    articles = []
    article_num = 0

    for category, count in categories_data:
        for i in range(count):
            article = create_sample_article(
                id=f"cat_{article_num:03d}",
                title=f"{category} News {i+1}",
                source=source,
                category=category,
            )
            articles.append(article)
            article_num += 1

    return articles


def create_articles_with_images() -> list:
    """Create articles with varying image availability."""
    source = create_sample_source()

    articles = []
    for i in range(6):
        article = create_sample_article(
            id=f"img_{i:03d}",
            title=f"Image Test Article {i+1}",
            source=source,
        )

        # Vary image availability
        if i % 3 == 0:
            article.image_url = f"https://example.com/image_{i}.jpg"
            article.generated_image_url = None
        elif i % 3 == 1:
            article.image_url = None
            article.generated_image_url = f"https://ai.example.com/gen_{i}.jpg"
        else:
            article.image_url = None
            article.generated_image_url = None

        articles.append(article)

    return articles


def create_articles_for_timeliness_test() -> list:
    """Create articles with varying ages for timeliness testing."""
    source = create_sample_source()

    ages = [
        timedelta(minutes=30),      # Very fresh
        timedelta(hours=2),         # Fresh
        timedelta(hours=12),        # Same day
        timedelta(days=1),          # Yesterday
        timedelta(days=3),          # Few days old
        timedelta(weeks=1),         # Week old
        timedelta(weeks=4),         # Month old
    ]

    articles = []
    for i, age in enumerate(ages):
        article = create_sample_article(
            id=f"time_{i:03d}",
            title=f"Article from {age} ago",
            source=source,
            scraped_at=datetime.now() - age,
        )
        articles.append(article)

    return articles

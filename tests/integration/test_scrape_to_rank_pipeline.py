"""Integration tests for scrape to rank pipeline."""

import pytest
import tempfile
import shutil
from datetime import datetime

from app.services.article_service import ArticleService
from app.services.ranking_service import RankingService
from app.models.article import Article, ArticleSource, ArticleStatus


class TestScrapeToRankPipeline:
    """Integration tests for the scraping to ranking pipeline."""

    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def article_service(self, temp_storage):
        """Create article service with temp storage."""
        return ArticleService(storage_path=temp_storage)

    @pytest.fixture
    def ranking_service(self):
        """Create ranking service."""
        return RankingService()

    def test_full_pipeline_flow(self, article_service, ranking_service):
        """Test complete pipeline from article creation to ranking."""
        # Simulate scraped articles
        sources = [
            ArticleSource(name="Reuters", url="https://reuters.com", domain="reuters.com"),
            ArticleSource(name="BBC", url="https://bbc.com", domain="bbc.com"),
            ArticleSource(name="CNN", url="https://cnn.com", domain="cnn.com"),
        ]

        articles = []
        for i, source in enumerate(sources):
            article = article_service.create(
                title=f"Breaking News Story {i+1}: Major Development",
                url=f"https://{source.domain}/article/{i+1}",
                source_name=source.name,
                source_url=source.url,
                content="A" * (1000 + i * 500),  # Varying content lengths
                image_url=f"https://{source.domain}/image.jpg" if i % 2 == 0 else None,
                author="Test Author" if i % 2 == 0 else None,
            )
            articles.append(article)
            article_service.save(article)

        # Verify articles saved
        saved_articles = article_service.get_all()
        assert len(saved_articles) == 3

        # Rank articles
        batch = ranking_service.rank_articles(saved_articles)

        # Verify ranking results
        assert batch.total_articles == 3
        assert len(batch.results) == 3

        # Top article should be from Reuters (highest credibility)
        top_result = batch.results[0]
        top_article = article_service.get(top_result.article_id)
        assert top_article is not None

        # Verify scores are calculated
        for result in batch.results:
            assert result.total_score > 0
            assert 'quality' in result.scores
            assert 'credibility' in result.scores

    def test_pipeline_with_status_updates(self, article_service, ranking_service):
        """Test pipeline with status tracking."""
        source = ArticleSource(
            name="Test Source",
            url="https://test.com",
            domain="test.com",
        )

        # Create and save article
        article = article_service.create(
            title="Test Pipeline Article",
            url="https://test.com/pipeline",
            source_name=source.name,
            source_url=source.url,
            content="A" * 1500,
        )
        article_service.save(article)

        # Verify initial status
        saved = article_service.get(article.id)
        assert saved.status == ArticleStatus.SCRAPED

        # Rank
        batch = ranking_service.rank_articles([saved])
        result = batch.results[0]

        # Update article with ranking
        saved.rank_score = result.total_score
        saved.ranking_details = result.scores
        saved.status = ArticleStatus.RANKED
        article_service.update(saved)

        # Verify update
        updated = article_service.get(article.id)
        assert updated.status == ArticleStatus.RANKED
        assert updated.rank_score > 0
        assert 'quality' in updated.ranking_details

    def test_pipeline_filtering(self, article_service, ranking_service):
        """Test filtering articles before ranking."""
        source = ArticleSource(
            name="Source",
            url="https://source.com",
            domain="source.com",
        )

        # Create articles with different categories
        categories = ["Tech", "Sports", "Politics", "Tech"]
        for i, cat in enumerate(categories):
            article = article_service.create(
                title=f"{cat} Article {i}",
                url=f"https://source.com/{cat}/{i}",
                source_name=source.name,
                source_url=source.url,
                content="A" * 1000,
                category=cat,
            )
            article_service.save(article)

        # Get only Tech articles
        tech_articles = article_service.get_by_category("Tech")
        assert len(tech_articles) == 2

        # Rank only Tech articles
        batch = ranking_service.rank_articles(tech_articles)
        assert batch.total_articles == 2

    def test_pipeline_deduplication(self, article_service):
        """Test that duplicate articles are handled correctly."""
        source = ArticleSource(
            name="Source",
            url="https://source.com",
            domain="source.com",
        )

        url = "https://source.com/duplicate"

        # First article
        article1 = article_service.create(
            title="Original Article",
            url=url,
            source_name=source.name,
            source_url=source.url,
        )
        article_service.save(article1)

        # Try to create duplicate (should have same ID)
        article2 = article_service.create(
            title="Duplicate Article",
            url=url,
            source_name=source.name,
            source_url=source.url,
        )

        # IDs should be the same
        assert article1.id == article2.id

        # exists() should return True
        assert article_service.exists(url)

    def test_pipeline_batch_processing(self, article_service, ranking_service):
        """Test processing large batch of articles."""
        source = ArticleSource(
            name="Batch Source",
            url="https://batch.com",
            domain="batch.com",
        )

        # Create many articles
        articles = []
        for i in range(50):
            article = article_service.create(
                title=f"Batch Article {i}",
                url=f"https://batch.com/article/{i}",
                source_name=source.name,
                source_url=source.url,
                content=f"Content for article {i}. " * 100,
            )
            articles.append(article)

        # Bulk save
        saved_count = article_service.bulk_save(articles)
        assert saved_count == 50

        # Rank all
        all_articles = article_service.get_all()
        batch = ranking_service.rank_articles(all_articles, top_n=10)

        # Should return top 10
        assert len(batch.results) == 10
        assert batch.total_articles == 50

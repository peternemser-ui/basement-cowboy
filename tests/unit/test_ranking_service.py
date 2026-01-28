"""Tests for RankingService."""

import pytest
from datetime import datetime, timedelta

from app.services.ranking_service import RankingService
from app.models.article import Article, ArticleSource
from app.models.ranking import RankingWeights


class TestRankingService:
    """Tests for RankingService."""

    @pytest.fixture
    def service(self):
        """Create RankingService instance."""
        return RankingService()

    @pytest.fixture
    def sample_source(self):
        """Create sample ArticleSource."""
        return ArticleSource(
            name="Reuters",
            url="https://reuters.com",
            domain="reuters.com",
        )

    @pytest.fixture
    def sample_articles(self, sample_source):
        """Create sample articles for testing."""
        now = datetime.now()
        return [
            Article(
                id="a1",
                title="Breaking: Major Economic News Released Today",
                url="https://reuters.com/article1",
                source=sample_source,
                content="A" * 2500,  # Long content
                image_url="https://example.com/image1.jpg",
                author="John Reporter",
                scraped_at=now - timedelta(hours=1),
            ),
            Article(
                id="a2",
                title="Short title",
                url="https://reuters.com/article2",
                source=sample_source,
                content="B" * 500,  # Short content
                scraped_at=now - timedelta(hours=12),
            ),
            Article(
                id="a3",
                title="You Won't Believe This Amazing Story!!!",  # Clickbait
                url="https://reuters.com/article3",
                source=sample_source,
                content="C" * 1500,
                scraped_at=now - timedelta(days=3),
            ),
        ]

    def test_rank_articles(self, service, sample_articles):
        """Test ranking a list of articles."""
        batch = service.rank_articles(sample_articles)

        assert batch.total_articles == 3
        assert len(batch.results) == 3
        assert batch.processing_time_ms > 0

    def test_ranking_order(self, service, sample_articles):
        """Test that articles are ranked in correct order."""
        batch = service.rank_articles(sample_articles)
        results = batch.results

        # First article should have highest score (good content)
        assert results[0].article_id == "a1"

        # Scores should be in descending order
        for i in range(len(results) - 1):
            assert results[i].total_score >= results[i + 1].total_score

    def test_ranking_positions(self, service, sample_articles):
        """Test that rank positions are assigned correctly."""
        batch = service.rank_articles(sample_articles)

        for i, result in enumerate(batch.results):
            assert result.rank_position == i + 1

    def test_percentiles(self, service, sample_articles):
        """Test percentile calculation."""
        batch = service.rank_articles(sample_articles)

        # Top article should have highest percentile
        assert batch.results[0].percentile > batch.results[-1].percentile

    def test_quality_score(self, service, sample_articles):
        """Test quality scoring."""
        batch = service.rank_articles(sample_articles)

        # Find the article with long content
        long_content_result = next(
            r for r in batch.results if r.article_id == "a1"
        )
        short_content_result = next(
            r for r in batch.results if r.article_id == "a2"
        )

        assert long_content_result.scores['quality'] > short_content_result.scores['quality']

    def test_credibility_score_known_source(self, service):
        """Test credibility scoring for known sources."""
        reuters_source = ArticleSource(
            name="Reuters",
            url="https://reuters.com",
            domain="reuters.com",
        )
        article = Article(
            id="test",
            title="Test",
            url="https://reuters.com/test",
            source=reuters_source,
        )

        batch = service.rank_articles([article])
        # Reuters should have high credibility
        assert batch.results[0].scores['credibility'] >= 0.9

    def test_timeliness_score(self, service, sample_source):
        """Test timeliness scoring."""
        now = datetime.now()
        fresh_article = Article(
            id="fresh",
            title="Fresh Article",
            url="https://example.com/fresh",
            source=sample_source,
            scraped_at=now - timedelta(minutes=30),
        )
        old_article = Article(
            id="old",
            title="Old Article",
            url="https://example.com/old",
            source=sample_source,
            scraped_at=now - timedelta(days=5),
        )

        batch = service.rank_articles([fresh_article, old_article])
        fresh_result = next(r for r in batch.results if r.article_id == "fresh")
        old_result = next(r for r in batch.results if r.article_id == "old")

        assert fresh_result.scores['timeliness'] > old_result.scores['timeliness']

    def test_visuals_score(self, service, sample_source):
        """Test visual content scoring."""
        with_image = Article(
            id="with_img",
            title="With Image",
            url="https://example.com/img",
            source=sample_source,
            image_url="https://example.com/image.jpg",
        )
        without_image = Article(
            id="no_img",
            title="No Image",
            url="https://example.com/no-img",
            source=sample_source,
        )

        batch = service.rank_articles([with_image, without_image])
        img_result = next(r for r in batch.results if r.article_id == "with_img")
        no_img_result = next(r for r in batch.results if r.article_id == "no_img")

        assert img_result.scores['visuals'] > no_img_result.scores['visuals']

    def test_custom_weights(self, service, sample_articles):
        """Test ranking with custom weights."""
        # Use quality-focused weights
        weights = RankingWeights.quality_focused()
        batch = service.rank_articles(sample_articles, weights=weights)

        assert batch.weights_used == weights
        # Results should still be valid
        assert len(batch.results) == 3

    def test_top_n_limit(self, service, sample_articles):
        """Test limiting results to top N."""
        batch = service.rank_articles(sample_articles, top_n=2)

        assert len(batch.results) == 2

    def test_clickbait_penalty(self, service, sample_source):
        """Test that clickbait titles receive lower quality scores."""
        clickbait = Article(
            id="clickbait",
            title="You Won't Believe What Happened Next!!!",
            url="https://example.com/clickbait",
            source=sample_source,
            content="A" * 1000,
        )
        normal = Article(
            id="normal",
            title="Economic Report Shows Steady Growth",
            url="https://example.com/normal",
            source=sample_source,
            content="A" * 1000,
        )

        batch = service.rank_articles([clickbait, normal])
        clickbait_result = next(r for r in batch.results if r.article_id == "clickbait")
        normal_result = next(r for r in batch.results if r.article_id == "normal")

        assert normal_result.scores['quality'] > clickbait_result.scores['quality']

    def test_explain_ranking(self, service, sample_articles):
        """Test generating ranking explanation."""
        batch = service.rank_articles(sample_articles)
        explanation = service.explain_ranking(batch.results[0])

        assert 'quality' in explanation
        assert 'credibility' in explanation
        assert 'timeliness' in explanation

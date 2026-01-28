"""Tests for Ranking models."""

import pytest
from app.models.ranking import RankingResult, RankingWeights, RankingCriteria, RankingBatch


class TestRankingWeights:
    """Tests for RankingWeights dataclass."""

    def test_default_weights(self):
        """Test default weights sum to 1.0."""
        weights = RankingWeights.default()
        total = (
            weights.quality + weights.credibility + weights.engagement +
            weights.visuals + weights.timeliness + weights.category_diversity +
            weights.geographic_diversity
        )
        assert abs(total - 1.0) < 0.01

    def test_quality_focused_preset(self):
        """Test quality focused preset."""
        weights = RankingWeights.quality_focused()
        assert weights.quality == 0.30
        assert weights.credibility == 0.30

    def test_engagement_focused_preset(self):
        """Test engagement focused preset."""
        weights = RankingWeights.engagement_focused()
        assert weights.engagement == 0.25
        assert weights.visuals == 0.20

    def test_invalid_weights_raise_error(self):
        """Test that invalid weights raise ValueError."""
        with pytest.raises(ValueError):
            RankingWeights(
                quality=0.5,
                credibility=0.5,
                engagement=0.5,  # Total > 1.0
                visuals=0.1,
                timeliness=0.1,
                category_diversity=0.1,
                geographic_diversity=0.1,
            )

    def test_weights_to_dict(self):
        """Test converting weights to dictionary."""
        weights = RankingWeights.default()
        data = weights.to_dict()
        assert 'quality' in data
        assert 'credibility' in data
        assert data['quality'] == 0.20

    def test_weights_from_dict(self):
        """Test creating weights from dictionary."""
        data = {
            'quality': 0.25,
            'credibility': 0.25,
            'engagement': 0.15,
            'visuals': 0.10,
            'timeliness': 0.10,
            'category_diversity': 0.08,
            'geographic_diversity': 0.07,
        }
        weights = RankingWeights.from_dict(data)
        assert weights.quality == 0.25
        assert weights.credibility == 0.25


class TestRankingResult:
    """Tests for RankingResult dataclass."""

    def test_create_result(self):
        """Test creating a ranking result."""
        result = RankingResult(
            article_id="test123",
            total_score=0.85,
            scores={'quality': 0.9, 'credibility': 0.8},
        )
        assert result.article_id == "test123"
        assert result.total_score == 0.85
        assert result.scores['quality'] == 0.9

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = RankingResult(
            article_id="test456",
            total_score=0.75,
            rank_position=5,
            percentile=85.0,
        )
        data = result.to_dict()
        assert data['article_id'] == "test456"
        assert data['total_score'] == 0.75
        assert data['rank_position'] == 5
        assert data['percentile'] == 85.0

    def test_result_from_dict(self):
        """Test creating result from dictionary."""
        data = {
            'article_id': 'abc789',
            'total_score': 0.92,
            'scores': {'quality': 0.95},
            'rank_position': 1,
        }
        result = RankingResult.from_dict(data)
        assert result.article_id == 'abc789'
        assert result.total_score == 0.92
        assert result.rank_position == 1


class TestRankingBatch:
    """Tests for RankingBatch dataclass."""

    @pytest.fixture
    def sample_results(self):
        """Create sample ranking results."""
        return [
            RankingResult(article_id="a1", total_score=0.95),
            RankingResult(article_id="a2", total_score=0.85),
            RankingResult(article_id="a3", total_score=0.75),
            RankingResult(article_id="a4", total_score=0.65),
            RankingResult(article_id="a5", total_score=0.55),
        ]

    def test_get_top(self, sample_results):
        """Test getting top N results."""
        batch = RankingBatch(results=sample_results, total_articles=5)
        top_3 = batch.get_top(3)
        assert len(top_3) == 3
        assert top_3[0].article_id == "a1"
        assert top_3[0].total_score == 0.95

    def test_get_top_more_than_available(self, sample_results):
        """Test getting more results than available."""
        batch = RankingBatch(results=sample_results, total_articles=5)
        top_10 = batch.get_top(10)
        assert len(top_10) == 5


class TestRankingCriteria:
    """Tests for RankingCriteria enum."""

    def test_criteria_values(self):
        """Test ranking criteria values."""
        assert RankingCriteria.QUALITY.value == "quality"
        assert RankingCriteria.CREDIBILITY.value == "credibility"
        assert RankingCriteria.ENGAGEMENT.value == "engagement"
        assert RankingCriteria.VISUALS.value == "visuals"
        assert RankingCriteria.TIMELINESS.value == "timeliness"

"""Ranking data models."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class RankingCriteria(Enum):
    """Available ranking criteria."""
    QUALITY = "quality"
    CREDIBILITY = "credibility"
    ENGAGEMENT = "engagement"
    VISUALS = "visuals"
    TIMELINESS = "timeliness"
    CATEGORY_DIVERSITY = "category_diversity"
    GEOGRAPHIC_DIVERSITY = "geographic_diversity"


@dataclass
class RankingWeights:
    """Weights for ranking criteria."""
    quality: float = 0.20
    credibility: float = 0.20
    engagement: float = 0.15
    visuals: float = 0.10
    timeliness: float = 0.15
    category_diversity: float = 0.10
    geographic_diversity: float = 0.10

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = (
            self.quality + self.credibility + self.engagement +
            self.visuals + self.timeliness + self.category_diversity +
            self.geographic_diversity
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def to_dict(self) -> Dict[str, float]:
        return {
            'quality': self.quality,
            'credibility': self.credibility,
            'engagement': self.engagement,
            'visuals': self.visuals,
            'timeliness': self.timeliness,
            'category_diversity': self.category_diversity,
            'geographic_diversity': self.geographic_diversity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'RankingWeights':
        return cls(**data)

    @classmethod
    def default(cls) -> 'RankingWeights':
        """Return default weights."""
        return cls()

    @classmethod
    def quality_focused(cls) -> 'RankingWeights':
        """Weights emphasizing quality and credibility."""
        return cls(
            quality=0.30,
            credibility=0.30,
            engagement=0.10,
            visuals=0.05,
            timeliness=0.10,
            category_diversity=0.08,
            geographic_diversity=0.07,
        )

    @classmethod
    def engagement_focused(cls) -> 'RankingWeights':
        """Weights emphasizing engagement and visuals."""
        return cls(
            quality=0.15,
            credibility=0.15,
            engagement=0.25,
            visuals=0.20,
            timeliness=0.10,
            category_diversity=0.08,
            geographic_diversity=0.07,
        )


@dataclass
class RankingResult:
    """Result of ranking an article."""
    article_id: str
    total_score: float
    scores: Dict[str, float] = field(default_factory=dict)
    weights_used: Optional[RankingWeights] = None
    rank_position: int = 0
    percentile: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'article_id': self.article_id,
            'total_score': self.total_score,
            'scores': self.scores,
            'weights_used': self.weights_used.to_dict() if self.weights_used else None,
            'rank_position': self.rank_position,
            'percentile': self.percentile,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RankingResult':
        weights = data.get('weights_used')
        if weights:
            weights = RankingWeights.from_dict(weights)
        return cls(
            article_id=data.get('article_id', ''),
            total_score=data.get('total_score', 0.0),
            scores=data.get('scores', {}),
            weights_used=weights,
            rank_position=data.get('rank_position', 0),
            percentile=data.get('percentile', 0.0),
        )


@dataclass
class RankingBatch:
    """Results from ranking a batch of articles."""
    results: List[RankingResult] = field(default_factory=list)
    total_articles: int = 0
    processing_time_ms: float = 0.0
    weights_used: Optional[RankingWeights] = None

    def get_top(self, n: int = 10) -> List[RankingResult]:
        """Get top N ranked articles."""
        sorted_results = sorted(self.results, key=lambda r: r.total_score, reverse=True)
        return sorted_results[:n]

    def get_by_category(self, category: str) -> List[RankingResult]:
        """Filter results by category."""
        return [r for r in self.results if r.scores.get('category') == category]

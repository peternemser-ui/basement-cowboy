"""Article ranking service."""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter

from app.models.article import Article
from app.models.ranking import RankingResult, RankingWeights, RankingBatch


class RankingService:
    """Service for ranking articles using a multi-factor algorithm."""

    # Known reliable sources with credibility scores
    CREDIBILITY_SCORES = {
        'reuters.com': 0.95,
        'apnews.com': 0.95,
        'bbc.com': 0.90,
        'bbc.co.uk': 0.90,
        'npr.org': 0.88,
        'pbs.org': 0.88,
        'nytimes.com': 0.85,
        'washingtonpost.com': 0.85,
        'theguardian.com': 0.85,
        'wsj.com': 0.85,
        'economist.com': 0.85,
        'cnn.com': 0.75,
        'foxnews.com': 0.70,
        'msnbc.com': 0.70,
    }

    def __init__(self, weights: Optional[RankingWeights] = None):
        self.weights = weights or RankingWeights.default()

    def rank_articles(
        self,
        articles: List[Article],
        weights: Optional[RankingWeights] = None,
        top_n: Optional[int] = None,
    ) -> RankingBatch:
        """Rank a list of articles."""
        start_time = datetime.now()
        weights = weights or self.weights

        results = []
        for article in articles:
            result = self._rank_single(article, weights)
            results.append(result)

        # Sort by score
        results.sort(key=lambda r: r.total_score, reverse=True)

        # Assign positions and percentiles
        total = len(results)
        for i, result in enumerate(results):
            result.rank_position = i + 1
            result.percentile = (total - i) / total * 100

        # Apply diversity bonus for top results
        results = self._apply_diversity_bonus(results, articles)

        # Limit results if requested
        if top_n:
            results = results[:top_n]

        elapsed = (datetime.now() - start_time).total_seconds() * 1000

        return RankingBatch(
            results=results,
            total_articles=len(articles),
            processing_time_ms=elapsed,
            weights_used=weights,
        )

    def _rank_single(self, article: Article, weights: RankingWeights) -> RankingResult:
        """Calculate ranking scores for a single article."""
        scores = {
            'quality': self._score_quality(article),
            'credibility': self._score_credibility(article),
            'engagement': self._score_engagement(article),
            'visuals': self._score_visuals(article),
            'timeliness': self._score_timeliness(article),
        }

        # Calculate weighted total
        total_score = (
            scores['quality'] * weights.quality +
            scores['credibility'] * weights.credibility +
            scores['engagement'] * weights.engagement +
            scores['visuals'] * weights.visuals +
            scores['timeliness'] * weights.timeliness
        )

        return RankingResult(
            article_id=article.id,
            total_score=total_score,
            scores=scores,
            weights_used=weights,
        )

    def _score_quality(self, article: Article) -> float:
        """Score article quality based on content characteristics."""
        score = 0.0

        # Content length (longer is generally better, up to a point)
        content_len = len(article.content)
        if content_len > 2000:
            score += 0.3
        elif content_len > 1000:
            score += 0.2
        elif content_len > 500:
            score += 0.1

        # Title quality
        title_len = len(article.title)
        if 40 <= title_len <= 100:
            score += 0.2  # Good headline length
        elif 20 <= title_len <= 120:
            score += 0.1

        # Has author attribution
        if article.author:
            score += 0.1

        # Has proper excerpt/summary
        if article.excerpt and len(article.excerpt) > 50:
            score += 0.1

        # Check for clickbait indicators (negative)
        clickbait_patterns = [
            r'\bYou Won\'t Believe\b',
            r'\bShocking\b',
            r'\bThis One Trick\b',
            r'\b\d+ (Things|Reasons|Ways)\b',
            r'!!+',
            r'\?\?+',
        ]
        title_lower = article.title.lower()
        for pattern in clickbait_patterns:
            if re.search(pattern, article.title, re.IGNORECASE):
                score -= 0.1

        # Check for professional writing indicators
        if article.content:
            # Proper paragraph structure
            paragraphs = article.content.split('\n\n')
            if len(paragraphs) >= 3:
                score += 0.1

            # Quotes (indicates sourcing)
            if '"' in article.content or "'" in article.content:
                score += 0.1

        return max(0, min(1, score))

    def _score_credibility(self, article: Article) -> float:
        """Score source credibility."""
        domain = article.source.domain.lower()

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        # Check known sources
        if domain in self.CREDIBILITY_SCORES:
            return self.CREDIBILITY_SCORES[domain]

        # Use source's reliability score if available
        if article.source.reliability_score:
            return article.source.reliability_score

        # Default score for unknown sources
        return 0.5

    def _score_engagement(self, article: Article) -> float:
        """Score potential engagement based on content analysis."""
        score = 0.5  # Base score

        # Title characteristics that drive engagement
        title = article.title.lower()

        # Question headlines
        if '?' in article.title:
            score += 0.1

        # Numbers in headline
        if re.search(r'\b\d+\b', article.title):
            score += 0.05

        # Trending topics (simplified check)
        trending_terms = ['ai', 'climate', 'election', 'economy', 'health', 'tech']
        for term in trending_terms:
            if term in title:
                score += 0.05

        # Breaking news indicator
        if 'breaking' in title:
            score += 0.1

        # Exclusive content
        if 'exclusive' in title:
            score += 0.1

        return min(1, score)

    def _score_visuals(self, article: Article) -> float:
        """Score visual content availability."""
        score = 0.0

        # Has main image
        if article.image_url:
            score += 0.5

        # Has AI-generated image
        if article.generated_image_url:
            score += 0.3

        # Has multiple images
        if len(article.images) > 1:
            score += 0.2

        return min(1, score)

    def _score_timeliness(self, article: Article) -> float:
        """Score article freshness."""
        if not article.scraped_at:
            return 0.5

        age = datetime.now() - article.scraped_at
        hours = age.total_seconds() / 3600

        # Score based on age
        if hours < 1:
            return 1.0
        elif hours < 6:
            return 0.9
        elif hours < 12:
            return 0.8
        elif hours < 24:
            return 0.7
        elif hours < 48:
            return 0.5
        elif hours < 72:
            return 0.3
        else:
            return 0.1

    def _apply_diversity_bonus(
        self,
        results: List[RankingResult],
        articles: List[Article],
    ) -> List[RankingResult]:
        """Apply diversity bonus to promote category and source variety."""
        # Create article lookup
        article_map = {a.id: a for a in articles}

        # Track seen categories and sources
        seen_categories: Counter = Counter()
        seen_sources: Counter = Counter()

        adjusted_results = []
        for result in results:
            article = article_map.get(result.article_id)
            if not article:
                adjusted_results.append(result)
                continue

            # Calculate diversity penalty (reduce score if category/source seen multiple times)
            category_count = seen_categories.get(article.category, 0)
            source_count = seen_sources.get(article.source.name, 0)

            diversity_penalty = (category_count * 0.02) + (source_count * 0.03)

            # Apply penalty
            result.total_score = max(0, result.total_score - diversity_penalty)
            result.scores['category_diversity'] = max(0, 1 - (category_count * 0.2))
            result.scores['geographic_diversity'] = max(0, 1 - (source_count * 0.2))

            # Update counters
            if article.category:
                seen_categories[article.category] += 1
            seen_sources[article.source.name] += 1

            adjusted_results.append(result)

        # Re-sort after diversity adjustment
        adjusted_results.sort(key=lambda r: r.total_score, reverse=True)
        return adjusted_results

    def get_top_by_category(
        self,
        articles: List[Article],
        category: str,
        limit: int = 5,
    ) -> List[RankingResult]:
        """Get top ranked articles for a specific category."""
        filtered = [a for a in articles if a.category == category]
        batch = self.rank_articles(filtered, top_n=limit)
        return batch.results

    def explain_ranking(self, result: RankingResult) -> Dict[str, str]:
        """Generate human-readable explanation of ranking."""
        explanations = {
            'quality': f"Content quality score: {result.scores.get('quality', 0):.2f}",
            'credibility': f"Source credibility: {result.scores.get('credibility', 0):.2f}",
            'engagement': f"Engagement potential: {result.scores.get('engagement', 0):.2f}",
            'visuals': f"Visual content: {result.scores.get('visuals', 0):.2f}",
            'timeliness': f"Freshness: {result.scores.get('timeliness', 0):.2f}",
        }
        return explanations

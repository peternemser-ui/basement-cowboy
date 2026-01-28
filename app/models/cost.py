"""Cost tracking models."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum


class APIProvider(Enum):
    """API providers for cost tracking."""
    OPENAI = "openai"
    WORDPRESS = "wordpress"
    OTHER = "other"


class UsageType(Enum):
    """Types of API usage."""
    CHAT_COMPLETION = "chat_completion"
    IMAGE_GENERATION = "image_generation"
    EMBEDDING = "embedding"
    MEDIA_UPLOAD = "media_upload"
    POST_CREATE = "post_create"


@dataclass
class APIUsage:
    """Single API usage record."""
    provider: APIProvider
    usage_type: UsageType
    timestamp: datetime = field(default_factory=datetime.now)

    # Token counts (for OpenAI)
    input_tokens: int = 0
    output_tokens: int = 0

    # Cost
    cost: float = 0.0

    # Context
    article_id: Optional[str] = None
    model: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'provider': self.provider.value,
            'usage_type': self.usage_type.value,
            'timestamp': self.timestamp.isoformat(),
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cost': self.cost,
            'article_id': self.article_id,
            'model': self.model,
            'success': self.success,
            'error_message': self.error_message,
        }


# OpenAI pricing (as of 2024)
OPENAI_PRICING = {
    'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},  # per 1K tokens
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    'gpt-4o': {'input': 0.005, 'output': 0.015},
    'dall-e-3': {'1024x1024': 0.04, '1024x1792': 0.08, '1792x1024': 0.08},
    'dall-e-2': {'1024x1024': 0.02, '512x512': 0.018, '256x256': 0.016},
}


@dataclass
class CostTracker:
    """Track API costs over time."""
    usages: List[APIUsage] = field(default_factory=list)
    daily_limit: float = 50.0
    monthly_limit: float = 500.0

    def add_usage(self, usage: APIUsage) -> None:
        """Add a usage record."""
        self.usages.append(usage)

    def add_chat_completion(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        article_id: Optional[str] = None,
    ) -> APIUsage:
        """Record a chat completion usage."""
        pricing = OPENAI_PRICING.get(model, {'input': 0.001, 'output': 0.002})
        cost = (input_tokens / 1000 * pricing['input']) + (output_tokens / 1000 * pricing['output'])

        usage = APIUsage(
            provider=APIProvider.OPENAI,
            usage_type=UsageType.CHAT_COMPLETION,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            article_id=article_id,
            model=model,
        )
        self.add_usage(usage)
        return usage

    def add_image_generation(
        self,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        article_id: Optional[str] = None,
    ) -> APIUsage:
        """Record an image generation usage."""
        pricing = OPENAI_PRICING.get(model, {})
        cost = pricing.get(size, 0.04)

        usage = APIUsage(
            provider=APIProvider.OPENAI,
            usage_type=UsageType.IMAGE_GENERATION,
            cost=cost,
            article_id=article_id,
            model=model,
        )
        self.add_usage(usage)
        return usage

    @property
    def total_cost(self) -> float:
        """Get total cost of all usages."""
        return sum(u.cost for u in self.usages)

    def daily_cost(self, day: Optional[date] = None) -> float:
        """Get cost for a specific day."""
        if day is None:
            day = date.today()
        return sum(u.cost for u in self.usages if u.timestamp.date() == day)

    def monthly_cost(self, year: Optional[int] = None, month: Optional[int] = None) -> float:
        """Get cost for a specific month."""
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        return sum(
            u.cost for u in self.usages
            if u.timestamp.year == year and u.timestamp.month == month
        )

    def is_daily_limit_reached(self) -> bool:
        """Check if daily limit is reached."""
        return self.daily_cost() >= self.daily_limit

    def is_monthly_limit_reached(self) -> bool:
        """Check if monthly limit is reached."""
        return self.monthly_cost() >= self.monthly_limit

    def can_spend(self, amount: float) -> bool:
        """Check if an amount can be spent."""
        return (
            self.daily_cost() + amount <= self.daily_limit and
            self.monthly_cost() + amount <= self.monthly_limit
        )

    def get_usage_by_type(self, usage_type: UsageType) -> List[APIUsage]:
        """Get usages by type."""
        return [u for u in self.usages if u.usage_type == usage_type]

    def get_usage_by_article(self, article_id: str) -> List[APIUsage]:
        """Get usages for a specific article."""
        return [u for u in self.usages if u.article_id == article_id]

    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            'total_cost': self.total_cost,
            'daily_cost': self.daily_cost(),
            'monthly_cost': self.monthly_cost(),
            'daily_limit': self.daily_limit,
            'monthly_limit': self.monthly_limit,
            'daily_remaining': max(0, self.daily_limit - self.daily_cost()),
            'monthly_remaining': max(0, self.monthly_limit - self.monthly_cost()),
            'total_requests': len(self.usages),
            'successful_requests': sum(1 for u in self.usages if u.success),
            'failed_requests': sum(1 for u in self.usages if not u.success),
            'by_type': {
                t.value: sum(u.cost for u in self.usages if u.usage_type == t)
                for t in UsageType
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            'usages': [u.to_dict() for u in self.usages],
            'summary': self.get_summary(),
        }

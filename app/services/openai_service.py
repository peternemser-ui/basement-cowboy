"""OpenAI integration service."""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from app.models.cost import CostTracker, APIUsage


@dataclass
class SummaryResult:
    """Result of generating a summary."""
    summary: str
    input_tokens: int
    output_tokens: int
    cost: float
    model: str


@dataclass
class ImageResult:
    """Result of generating an image."""
    url: str
    revised_prompt: Optional[str]
    cost: float
    model: str


class OpenAIService:
    """Service for OpenAI API integration."""

    SUMMARY_PROMPTS = {
        'concise': """Summarize this news article in 2-3 sentences. Focus on the key facts and main point.

Article:
{content}

Summary:""",
        'detailed': """Provide a detailed summary of this news article in 4-5 sentences. Include key facts, context, and significance.

Article:
{content}

Summary:""",
        'bullet_points': """Summarize this news article as 3-5 bullet points. Each point should capture a key fact or development.

Article:
{content}

Summary:""",
    }

    IMAGE_PROMPT_TEMPLATE = """Create a professional news illustration for an article about: {topic}

Style: Photorealistic editorial illustration suitable for a news website
Mood: Professional, informative, engaging
Important: No text or words in the image"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        chat_model: str = "gpt-3.5-turbo",
        image_model: str = "dall-e-3",
    ):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.chat_model = chat_model
        self.image_model = image_model
        self.cost_tracker = CostTracker()
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package is required. Install with: pip install openai")
        return self._client

    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def generate_summary(
        self,
        content: str,
        style: str = "concise",
        article_id: Optional[str] = None,
    ) -> SummaryResult:
        """Generate an article summary."""
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        prompt_template = self.SUMMARY_PROMPTS.get(style, self.SUMMARY_PROMPTS['concise'])
        prompt = prompt_template.format(content=content[:4000])  # Limit content length

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a professional news editor. Provide clear, accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.5,
            )

            message = response.choices[0].message
            usage = response.usage

            # Track cost
            cost_record = self.cost_tracker.add_chat_completion(
                model=self.chat_model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                article_id=article_id,
            )

            return SummaryResult(
                summary=message.content.strip(),
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost=cost_record.cost,
                model=self.chat_model,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {str(e)}")

    def generate_image(
        self,
        prompt: Optional[str] = None,
        topic: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        article_id: Optional[str] = None,
    ) -> ImageResult:
        """Generate an image using DALL-E."""
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        # Use provided prompt or generate from topic
        if not prompt and topic:
            prompt = self.IMAGE_PROMPT_TEMPLATE.format(topic=topic)
        elif not prompt:
            raise ValueError("Either prompt or topic must be provided")

        try:
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )

            image_data = response.data[0]

            # Track cost
            cost_record = self.cost_tracker.add_image_generation(
                model=self.image_model,
                size=size,
                article_id=article_id,
            )

            return ImageResult(
                url=image_data.url,
                revised_prompt=getattr(image_data, 'revised_prompt', None),
                cost=cost_record.cost,
                model=self.image_model,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {str(e)}")

    def improve_headline(
        self,
        headline: str,
        content: str = "",
        article_id: Optional[str] = None,
    ) -> str:
        """Suggest an improved headline."""
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Improve this news headline to be more engaging while remaining accurate and professional.

Original headline: {headline}

Article context: {content[:500]}

Provide only the improved headline, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a professional news headline editor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7,
            )

            # Track cost
            usage = response.usage
            self.cost_tracker.add_chat_completion(
                model=self.chat_model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                article_id=article_id,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to improve headline: {str(e)}")

    def extract_keywords(
        self,
        content: str,
        max_keywords: int = 10,
        article_id: Optional[str] = None,
    ) -> List[str]:
        """Extract keywords from article content."""
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Extract the {max_keywords} most important keywords or phrases from this article.
Return them as a comma-separated list.

Article: {content[:2000]}

Keywords:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3,
            )

            # Track cost
            usage = response.usage
            self.cost_tracker.add_chat_completion(
                model=self.chat_model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                article_id=article_id,
            )

            keywords_str = response.choices[0].message.content.strip()
            keywords = [k.strip() for k in keywords_str.split(',')]
            return keywords[:max_keywords]
        except Exception as e:
            raise RuntimeError(f"Failed to extract keywords: {str(e)}")

    def categorize_article(
        self,
        title: str,
        content: str,
        categories: List[str],
        article_id: Optional[str] = None,
    ) -> str:
        """Categorize an article into one of the given categories."""
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        categories_str = ", ".join(categories)
        prompt = f"""Categorize this news article into exactly one of these categories: {categories_str}

Title: {title}
Content: {content[:1000]}

Category:"""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20,
                temperature=0.3,
            )

            # Track cost
            usage = response.usage
            self.cost_tracker.add_chat_completion(
                model=self.chat_model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                article_id=article_id,
            )

            category = response.choices[0].message.content.strip()
            # Validate category
            if category in categories:
                return category
            # Try to match partial
            for cat in categories:
                if cat.lower() in category.lower():
                    return cat
            return categories[0]  # Default to first category
        except Exception as e:
            raise RuntimeError(f"Failed to categorize article: {str(e)}")

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary."""
        return self.cost_tracker.get_summary()

    def can_afford(self, estimated_cost: float) -> bool:
        """Check if we can afford an operation."""
        return self.cost_tracker.can_spend(estimated_cost)

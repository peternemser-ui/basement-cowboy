"""
SEO Generator Module
Generates schema markup, meta tags, and SEO optimizations for WordPress articles
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
import logging

class SEOGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_article_schema(self, article: Dict[str, Any], author: str = "Basement Cowboy", 
                              organization: str = "Basement Cowboy News") -> Dict[str, Any]:
        """Generate JSON-LD schema markup for a news article"""
        
        # Clean and prepare content
        headline = self.clean_text(article.get('headline', ''))
        summary = self.clean_text(article.get('summary', ''))
        
        # Generate schema
        schema = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": headline,
            "description": summary,
            "author": {
                "@type": "Person",
                "name": author
            },
            "publisher": {
                "@type": "Organization", 
                "name": organization,
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://basementcowboy.com/wp-content/uploads/logo.png"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": article.get('link', '')
            }
        }
        
        # Add image if available
        if article.get('photo'):
            schema["image"] = {
                "@type": "ImageObject",
                "url": article['photo'],
                "width": 1200,
                "height": 630
            }
        
        # Add article section/category
        if article.get('category'):
            schema["articleSection"] = article['category']
        
        # Add keywords from summary
        keywords = self.extract_keywords(summary)
        if keywords:
            schema["keywords"] = keywords
        
        return schema
    
    def generate_breadcrumb_schema(self, category: str) -> Dict[str, Any]:
        """Generate breadcrumb schema for navigation"""
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://basementcowboy.com"
                },
                {
                    "@type": "ListItem", 
                    "position": 2,
                    "name": category,
                    "item": f"https://basementcowboy.com/category/{category.lower().replace(' ', '-')}"
                }
            ]
        }
    
    def generate_meta_tags(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate meta tags for SEO"""
        headline = self.clean_text(article.get('headline', ''))
        summary = self.clean_text(article.get('summary', ''))
        
        # Generate SEO title (max 60 characters)
        seo_title = self.optimize_title(headline)
        
        # Generate meta description (max 160 characters)
        meta_description = self.optimize_description(summary)
        
        meta_tags = {
            'title': seo_title,
            'meta_description': meta_description,
            'og_title': headline,
            'og_description': summary[:200] + '...' if len(summary) > 200 else summary,
            'og_type': 'article',
            'twitter_card': 'summary_large_image',
            'twitter_title': headline,
            'twitter_description': meta_description
        }
        
        # Add image meta tags
        if article.get('photo'):
            meta_tags.update({
                'og_image': article['photo'],
                'twitter_image': article['photo']
            })
        
        # Add category
        if article.get('category'):
            meta_tags['article_section'] = article['category']
        
        return meta_tags
    
    def generate_focus_keywords(self, article: Dict[str, Any]) -> List[str]:
        """Generate focus keywords for SEO optimization"""
        text = f"{article.get('headline', '')} {article.get('summary', '')}"
        keywords = self.extract_keywords(text)
        
        # Prioritize keywords by importance
        focus_keywords = []
        
        # Add category as primary keyword
        if article.get('category'):
            focus_keywords.append(article['category'].lower())
        
        # Add extracted keywords (top 5)
        focus_keywords.extend(keywords[:5])
        
        return list(set(focus_keywords))  # Remove duplicates
    
    def generate_seo_optimized_content(self, articles: List[Dict[str, Any]], 
                                     category: str) -> Dict[str, Any]:
        """Generate SEO-optimized content structure for WordPress post"""
        
        # Generate overall post meta
        post_title = f"Latest {category} News - {datetime.now().strftime('%B %d, %Y')}"
        post_description = f"Breaking {category.lower()} news and updates. Stay informed with the latest developments in {category.lower()}."
        
        # Generate combined schema for all articles
        article_schemas = []
        all_keywords = set()
        
        for article in articles:
            schema = self.generate_article_schema(article)
            article_schemas.append(schema)
            
            # Collect keywords
            keywords = self.extract_keywords(f"{article.get('headline', '')} {article.get('summary', '')}")
            all_keywords.update(keywords)
        
        # Create collection schema
        collection_schema = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "headline": post_title,
            "description": post_description,
            "mainEntity": article_schemas,
            "breadcrumb": self.generate_breadcrumb_schema(category)
        }
        
        # Generate post meta tags
        post_meta = {
            'title': self.optimize_title(post_title),
            'meta_description': self.optimize_description(post_description),
            'og_title': post_title,
            'og_description': post_description,
            'og_type': 'website',
            'twitter_card': 'summary',
            'twitter_title': post_title,
            'twitter_description': self.optimize_description(post_description),
            'keywords': ', '.join(list(all_keywords)[:10])  # Top 10 keywords
        }
        
        return {
            'post_meta': post_meta,
            'schema_markup': collection_schema,
            'individual_schemas': article_schemas,
            'focus_keywords': list(all_keywords)[:10],
            'readability_score': self.calculate_readability_score(articles)
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text for SEO optimization"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters that might break JSON
        text = text.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
        
        return text
    
    def optimize_title(self, title: str, max_length: int = 60) -> str:
        """Optimize title for SEO (max 60 characters)"""
        title = self.clean_text(title)
        
        if len(title) <= max_length:
            return title
        
        # Truncate at word boundary
        words = title.split()
        optimized = ""
        
        for word in words:
            if len(optimized + word + " ") <= max_length - 3:  # Leave room for "..."
                optimized += word + " "
            else:
                break
        
        return optimized.strip() + "..."
    
    def optimize_description(self, description: str, max_length: int = 160) -> str:
        """Optimize description for SEO (max 160 characters)"""
        description = self.clean_text(description)
        
        if len(description) <= max_length:
            return description
        
        # Truncate at word boundary
        words = description.split()
        optimized = ""
        
        for word in words:
            if len(optimized + word + " ") <= max_length - 3:
                optimized += word + " "
            else:
                break
        
        return optimized.strip() + "..."
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text for SEO"""
        if not text:
            return []
        
        # Clean text
        text = self.clean_text(text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (minimum 3 characters)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        
        # Filter stop words and count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
    
    def calculate_readability_score(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate readability scores for content"""
        total_words = 0
        total_sentences = 0
        total_syllables = 0
        
        for article in articles:
            text = f"{article.get('headline', '')} {article.get('summary', '')}"
            text = self.clean_text(text)
            
            words = len(text.split())
            sentences = len(re.findall(r'[.!?]+', text))
            syllables = self.count_syllables(text)
            
            total_words += words
            total_sentences += sentences
            total_syllables += syllables
        
        if total_sentences == 0 or total_words == 0:
            return {'score': 0, 'level': 'Unknown'}
        
        # Flesch Reading Ease Score
        score = 206.835 - (1.015 * (total_words / total_sentences)) - (84.6 * (total_syllables / total_words))
        
        # Determine reading level
        if score >= 90:
            level = "Very Easy"
        elif score >= 80:
            level = "Easy"
        elif score >= 70:
            level = "Fairly Easy"
        elif score >= 60:
            level = "Standard"
        elif score >= 50:
            level = "Fairly Difficult"
        elif score >= 30:
            level = "Difficult"
        else:
            level = "Very Difficult"
        
        return {
            'score': round(score, 1),
            'level': level,
            'words': total_words,
            'sentences': total_sentences,
            'avg_words_per_sentence': round(total_words / total_sentences, 1)
        }
    
    def count_syllables(self, text: str) -> int:
        """Count syllables in text (approximation)"""
        text = text.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in text:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent 'e'
        if text.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least 1 syllable per word
        word_count = len(text.split())
        if syllable_count < word_count:
            syllable_count = word_count
        
        return syllable_count
    
    def generate_seo_metadata(self, articles: List[Dict[str, Any]], category: str = "News") -> Dict[str, Any]:
        """Main method to generate SEO metadata - wrapper for generate_seo_optimized_content"""
        return self.generate_seo_optimized_content(articles, category)
    
    def generate_wordpress_seo_metadata(self, seo_data: Dict[str, Any]) -> str:
        """Generate WordPress-compatible SEO metadata"""
        
        meta_html = []
        
        # Schema markup
        if 'schema_markup' in seo_data:
            meta_html.append(f'<script type="application/ld+json">')
            meta_html.append(json.dumps(seo_data['schema_markup'], indent=2))
            meta_html.append('</script>')
        
        # Meta tags
        if 'post_meta' in seo_data:
            meta = seo_data['post_meta']
            
            # Basic meta tags
            if meta.get('meta_description'):
                meta_html.append(f'<meta name="description" content="{meta["meta_description"]}">')
            
            if meta.get('keywords'):
                meta_html.append(f'<meta name="keywords" content="{meta["keywords"]}">')
            
            # Open Graph tags
            if meta.get('og_title'):
                meta_html.append(f'<meta property="og:title" content="{meta["og_title"]}">')
            
            if meta.get('og_description'):
                meta_html.append(f'<meta property="og:description" content="{meta["og_description"]}">')
            
            if meta.get('og_type'):
                meta_html.append(f'<meta property="og:type" content="{meta["og_type"]}">')
            
            # Twitter Card tags
            if meta.get('twitter_card'):
                meta_html.append(f'<meta name="twitter:card" content="{meta["twitter_card"]}">')
            
            if meta.get('twitter_title'):
                meta_html.append(f'<meta name="twitter:title" content="{meta["twitter_title"]}">')
            
            if meta.get('twitter_description'):
                meta_html.append(f'<meta name="twitter:description" content="{meta["twitter_description"]}">')
        
        return '\n'.join(meta_html)
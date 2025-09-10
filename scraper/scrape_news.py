import os
import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from hashlib import sha256
from urllib.parse import urljoin

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# File paths
SOURCE_FILE = "config/top_100_news_sites.txt"
OUTPUT_DIR = "output/news_articles"

def fetch_with_retries(url, retries=3):
    """Fetch the URL with retries and headers to mimic a browser."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.warning(f"Error fetching {url} (attempt {attempt + 1}/{retries}): {e}")
    return None

def is_valid_news_article(headline, link):
    """Check if the link and headline suggest valid news content."""
    if len(headline) < 15:  # Restore stricter filtering
        logging.debug(f"Headline too short: {headline}")
        return False
    
    # Exclude navigation, utility pages, and non-article content
    exclude_patterns = [
        "ads", "signup", "subscribe", "login", "author", "mailto:", "javascript:", "#",
        "newsletter", "privacy", "terms", "contact", "about", "careers", "advertise",
        "trending videos", "live updates", "entertainment", "newsletters", "podcasts",
        "culture", "style", "sports", "technology", "business", "politics", "world",
        "international", "health", "science", "travel", "food", "weather",
        "gallery", "photos", "video", "alerts", "live-news", "shop", "games"
    ]
    
    headline_lower = headline.lower()
    link_lower = link.lower()
    
    # Check for excluded patterns in both headline and link
    if any(pattern in link_lower for pattern in exclude_patterns):
        logging.debug(f"Link contains excluded pattern: {link}")
        return False
    
    if any(pattern in headline_lower for pattern in exclude_patterns):
        logging.debug(f"Headline contains excluded pattern: {headline}")
        return False
    
    # Look for news article indicators
    news_indicators = [
        'story', 'article', 'news', 'report', 'breaking', 'update', 'says', 'dies',
        'killed', 'arrest', 'court', 'government', 'president', 'minister', 'war',
        'attack', 'fire', 'crash', 'murder', 'death', 'hospital', 'school', 'police'
    ]
    
    # Must be a proper HTTP link
    if not link.startswith(('http://', 'https://')):
        return False
    
    # Check if headline suggests it's a news article
    has_news_content = any(indicator in headline_lower for indicator in news_indicators)
    
    # Check link structure (should have path that suggests an article)
    has_article_structure = any(part in link_lower for part in ['/story/', '/news/', '/article/', '/politics/', '/world/'])
    
    # Accept if it has news content or proper structure, and proper length
    if (has_news_content or has_article_structure) and len(headline.strip()) >= 15:
        return True
    
    return False

def summarize_article(text):
    """Summarize text using intelligent extraction or OpenAI."""
    if not text or len(text.strip()) < 50:
        return "No content available"
    
    # Clean the text
    text = text.strip()
    
    if not OPENAI_API_KEY:
        # Smart fallback: get the first 2-3 sentences that contain substantial content
        sentences = text.split('. ')
        summary_sentences = []
        char_count = 0
        
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and char_count < 200:  # Substantial sentence
                summary_sentences.append(sentence)
                char_count += len(sentence)
                if len(summary_sentences) >= 2:  # Get 2 good sentences
                    break
        
        if summary_sentences:
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            return summary
        else:
            # Fallback to first 150 chars
            return text[:150] + "..." if len(text) > 150 else text

    try:
        # TODO: Add OpenAI API integration here when ready
        # For now, use the smart fallback
        sentences = text.split('. ')
        summary_sentences = []
        char_count = 0
        
        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 20 and char_count < 200:
                summary_sentences.append(sentence)
                char_count += len(sentence)
                if len(summary_sentences) >= 2:
                    break
        
        if summary_sentences:
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            return summary
        else:
            return text[:150] + "..." if len(text) > 150 else text
            
    except Exception as e:
        logging.error(f"Failed to summarize article: {e}")
        return text[:150] + "..." if len(text) > 150 else text

def fetch_article_details(url):
    """Fetch extended details like photos, detailed summary, and metadata."""
    try:
        response = fetch_with_retries(url)
        if not response:
            return {}

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for article images (avoid logos and small images)
        image_url = None
        for img in soup.find_all('img'):
            if 'src' in img.attrs:
                img_src = img['src']
                # Skip logos, icons, and small images
                if any(skip in img_src.lower() for skip in ['logo', 'icon', 'svg', 'disney', 'footer']):
                    continue
                
                # Prefer images with 'article', 'story', or large dimensions
                if any(good in img_src.lower() for good in ['article', 'story', 'news']) or \
                   (img.get('width') and int(img.get('width', '0')) > 300):
                    if not img_src.startswith(('http://', 'https://')):
                        img_src = urljoin(url, img_src)
                    image_url = img_src
                    break
        
        # If no good image found, get the first reasonable one
        if not image_url:
            for img in soup.find_all('img'):
                if 'src' in img.attrs:
                    img_src = img['src']
                    if not any(skip in img_src.lower() for skip in ['logo', 'icon', 'svg', 'disney', 'footer']):
                        if not img_src.startswith(('http://', 'https://')):
                            img_src = urljoin(url, img_src)
                        image_url = img_src
                        break

        # Extract article content more intelligently
        article_content = ""
        
        # Try to find article content in common containers
        content_selectors = [
            'article', '[class*="content"]', '[class*="story"]', 
            '[class*="article"]', 'main', '[role="main"]'
        ]
        
        for selector in content_selectors:
            content_container = soup.select_one(selector)
            if content_container:
                paragraphs = content_container.find_all('p')
                article_content = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
                if len(article_content) > 100:  # Found substantial content
                    break
        
        # Fallback: get all paragraphs
        if len(article_content) < 100:
            paragraphs = soup.find_all('p')
            article_content = " ".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)

        return {
            "detailed_summary": summarize_article(article_content) if article_content else "Content not available",
            "photo": image_url
        }
    except Exception as e:
        logging.error(f"Failed to fetch article details from {url}: {e}")
        return {"detailed_summary": "No details available", "photo": None}

def scrape_site(url):
    """Scrape a single site and extract articles with extended details."""
    logging.info(f"Scraping {url}")
    try:
        response = fetch_with_retries(url)
        if not response:
            logging.warning(f"Failed to fetch {url}")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        seen_hashes = set()
        link_count = 0

        for link in soup.find_all('a', href=True):
            link_count += 1
            headline = link.get_text(strip=True)
            href = link['href']

            if headline and href:
                # Make relative URLs absolute
                if not href.startswith(('http://', 'https://')):
                    from urllib.parse import urljoin
                    href = urljoin(url, href)
                
                if is_valid_news_article(headline, href):
                    unique_hash = sha256((headline + href).encode()).hexdigest()
                    if unique_hash not in seen_hashes:
                        seen_hashes.add(unique_hash)
                        logging.debug(f"Valid article found: {headline[:50]}...")
                        article_details = fetch_article_details(href)
                        articles.append({
                            "headline": headline,
                            "link": href,
                            "summary": summarize_article(headline),
                            "detailed_summary": article_details.get("detailed_summary"),
                            "photo": article_details.get("photo"),
                            "category": "Uncategorized"
                        })
                else:
                    logging.debug(f"Article filtered out: {headline[:30]}...")
        
        logging.info(f"Processed {link_count} links, found {len(articles)} valid articles from {url}")
        return articles
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {e}")
        return []

def scrape_news_sites():
    """Main function to scrape all news sites."""
    if not os.path.exists(SOURCE_FILE):
        logging.error(f"Source file not found: {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r') as file:
        news_sites = [line.strip() for line in file.read().splitlines() if line.strip() and not line.strip().startswith('#')]
    
    logging.info(f"Found {len(news_sites)} active news sites to scrape")
    all_articles = []
    seen_urls = set()

    for site in news_sites:
        logging.info(f"Processing site: {site}")
        articles = scrape_site(site)
        logging.info(f"Found {len(articles)} articles from {site}")
        for article in articles:
            if article["link"] not in seen_urls:
                seen_urls.add(article["link"])
                all_articles.append(article)
        
    logging.info(f"Total unique articles collected: {len(all_articles)}")

    if all_articles:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Generate a serialized file name
        today = datetime.now().strftime("%Y-%m-%d")
        base_file_name = f"news_articles_{today}"
        existing_files = [
            f for f in os.listdir(OUTPUT_DIR)
            if f.startswith(base_file_name) and f.endswith('.json')
        ]
        if existing_files:
            # Extract existing suffixes
            suffixes = [
                int(f.split('-')[-1].split('.')[0]) for f in existing_files if '-' in f
            ]
            suffix = max(suffixes) + 1
        else:
            suffix = 1

        output_file = os.path.join(OUTPUT_DIR, f"{base_file_name}-{suffix}.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=4)
            logging.info(f"Scraping complete. Articles saved to {output_file}")
        except IOError as e:
            logging.error(f"Failed to save JSON file: {e}")
    else:
        logging.warning("No articles found. Nothing to save.")

if __name__ == "__main__":
    scrape_news_sites()

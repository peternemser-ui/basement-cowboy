#!/usr/bin/env python3
"""Quick test scraper for a few reliable news sites."""

import os
import sys
import json
import logging
from datetime import datetime

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.scrape_news import scrape_site

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def quick_scrape_test():
    """Test scraping with just a few reliable sites."""
    
    # Test sites that usually work well
    test_sites = [
        "https://www.bbc.com/news",
        "https://abcnews.go.com", 
        "https://www.reuters.com",
        "https://edition.cnn.com",
        "https://www.forbes.com"
    ]
    
    all_articles = []
    seen_urls = set()
    
    for site in test_sites:
        try:
            logging.info(f"Testing scraper on: {site}")
            articles = scrape_site(site)
            logging.info(f"Found {len(articles)} articles from {site}")
            
            for article in articles:
                if article["link"] not in seen_urls:
                    seen_urls.add(article["link"])
                    all_articles.append(article)
                    
        except Exception as e:
            logging.error(f"Error scraping {site}: {e}")
            continue
    
    logging.info(f"Total unique articles collected: {len(all_articles)}")
    
    if all_articles:
        # Save to output directory
        output_dir = "output/news_articles"
        os.makedirs(output_dir, exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        base_file_name = f"news_articles_{today}"
        existing_files = [
            f for f in os.listdir(output_dir)
            if f.startswith(base_file_name) and f.endswith('.json')
        ]
        
        if existing_files:
            suffixes = []
            for f in existing_files:
                if '-' in f:
                    try:
                        suffix_str = f.split('-')[-1].split('.')[0]
                        suffixes.append(int(suffix_str))
                    except (ValueError, IndexError):
                        continue
            suffix = max(suffixes) + 1 if suffixes else 1
        else:
            suffix = 1

        output_file = os.path.join(output_dir, f"{base_file_name}-{suffix}.json")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_articles, f, ensure_ascii=False, indent=4)
            logging.info(f"Test scraping complete! Articles saved to {output_file}")
            print(f"SUCCESS: Created {output_file} with {len(all_articles)} articles")
        except IOError as e:
            logging.error(f"Failed to save JSON file: {e}")
    else:
        logging.warning("No articles found during test scraping")

if __name__ == "__main__":
    quick_scrape_test()
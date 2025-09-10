import os
import json
import logging
from datetime import datetime
from modules.fetch_page import fetch_page_content
from modules.parse_articles import parse_articles_from_soup
from modules.filter_articles import is_valid_news_article

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# File paths
SOURCE_FILE = "config/top_100_news_sites.txt"
OUTPUT_DIR = "output"

def scrape_news_sites():
    """
    Scrape news sites for articles.
    """
    if not os.path.exists(SOURCE_FILE):
        logging.error(f"Source file not found: {SOURCE_FILE}")
        return

    with open(SOURCE_FILE, 'r') as file:
        news_sites = file.read().splitlines()

    all_articles = []

    for site in news_sites:
        logging.info(f"Scraping {site}")
        soup = fetch_page_content(site)

        if soup:
            articles = parse_articles_from_soup(soup)
            filtered_articles = [
                article for article in articles
                if is_valid_news_article(article["headline"], article["link"], article["summary"])
            ]
            all_articles.extend(filtered_articles)

    # Save results
    if all_articles:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = os.path.join(OUTPUT_DIR, f"news_articles_{today}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=4)
        logging.info(f"Articles saved to {output_file}")
    else:
        logging.warning("No valid articles found.")

if __name__ == "__main__":
    scrape_news_sites()

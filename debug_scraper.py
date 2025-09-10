#!/usr/bin/env python3
"""
Simple test with file output to debug scraping
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

def log_to_file(message):
    """Write debug messages to a file"""
    with open("scraper_debug.log", "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def test_scraping():
    """Test scraping with file logging"""
    
    log_to_file("=== Starting scraper test ===")
    
    # Read news sites
    sites_file = "config/top_100_news_sites.txt"
    if not os.path.exists(sites_file):
        log_to_file(f"ERROR: {sites_file} not found")
        return
    
    with open(sites_file, 'r') as f:
        sites = [line.strip() for line in f.read().splitlines() 
                if line.strip() and not line.strip().startswith('#')]
    
    log_to_file(f"Found {len(sites)} active sites: {sites}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_articles = []
    
    for site in sites:
        log_to_file(f"Processing site: {site}")
        
        try:
            response = requests.get(site, headers=headers, timeout=15)
            log_to_file(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                links = soup.find_all('a', href=True)
                log_to_file(f"Found {len(links)} links on {site}")
                
                valid_articles = 0
                for link in links:
                    headline = link.get_text(strip=True)
                    href = link['href']
                    
                    if len(headline) >= 10 and href:
                        # Make absolute URL
                        if not href.startswith(('http://', 'https://')):
                            href = urljoin(site, href)
                        
                        # Simple validation
                        exclude_patterns = ["ads", "signup", "subscribe", "login", "mailto:", "javascript:", "#"]
                        if not any(pattern in href.lower() for pattern in exclude_patterns):
                            if href.startswith(('http://', 'https://')):
                                all_articles.append({
                                    "headline": headline,
                                    "link": href,
                                    "summary": headline[:100] + "..." if len(headline) > 100 else headline,
                                    "category": "Uncategorized"
                                })
                                valid_articles += 1
                
                log_to_file(f"Valid articles from {site}: {valid_articles}")
            else:
                log_to_file(f"Failed to fetch {site}: HTTP {response.status_code}")
                
        except Exception as e:
            log_to_file(f"Error processing {site}: {str(e)}")
    
    log_to_file(f"Total articles collected: {len(all_articles)}")
    
    if all_articles:
        # Save to output directory
        os.makedirs("output/news_articles", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = f"output/news_articles/news_articles_{today}-debug.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        
        log_to_file(f"Articles saved to: {output_file}")
        
        # Also save a summary
        with open("scraper_summary.txt", "w", encoding="utf-8") as f:
            f.write(f"Scraping completed at {datetime.now()}\n")
            f.write(f"Total articles: {len(all_articles)}\n")
            f.write(f"Output file: {output_file}\n")
            f.write("\nFirst few articles:\n")
            for i, article in enumerate(all_articles[:5]):
                f.write(f"{i+1}. {article['headline'][:80]}...\n")
        
        log_to_file("=== Test completed successfully ===")
        return True
    else:
        log_to_file("=== No articles found ===")
        return False

if __name__ == "__main__":
    # Clear previous log
    if os.path.exists("scraper_debug.log"):
        os.remove("scraper_debug.log")
    
    test_scraping()

#!/usr/bin/env python3
"""
Direct test of news scraping functionality
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin

def test_scraper_direct():
    """Test scraper with direct output to console and file"""
    
    # Test sites
    sites = [
        "https://abcnews.go.com",
        "https://arstechnica.com", 
        "https://edition.cnn.com",
        "https://www.vice.com/en/topic/weird"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    all_articles = []
    
    for site in sites:
        print(f"\n=== Testing {site} ===")
        
        try:
            print("Making request...")
            response = requests.get(site, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Failed to fetch {site}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            links = soup.find_all('a', href=True)
            print(f"Found {len(links)} total links")
            
            site_articles = []
            
            for link in links:
                headline = link.get_text(strip=True)
                href = link['href']
                
                if len(headline) >= 10 and href:
                    # Make absolute URL
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(site, href)
                    
                    # Simple filtering
                    exclude_patterns = ["ads", "signup", "subscribe", "login", "author", "mailto:", "javascript:", "#"]
                    if not any(pattern in href.lower() for pattern in exclude_patterns):
                        if href.startswith(('http://', 'https://')):
                            site_articles.append({
                                "headline": headline,
                                "link": href,
                                "summary": headline[:100] + "..." if len(headline) > 100 else headline,
                                "category": "Uncategorized"
                            })
            
            print(f"Valid articles from {site}: {len(site_articles)}")
            all_articles.extend(site_articles)
            
            # Show first few articles found
            for i, article in enumerate(site_articles[:3]):
                print(f"  {i+1}. {article['headline'][:60]}...")
                
        except Exception as e:
            print(f"Error processing {site}: {e}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total articles found: {len(all_articles)}")
    
    if all_articles:
        # Save results
        os.makedirs("output/news_articles", exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        output_file = f"output/news_articles/news_articles_{today}-test.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
            
        print(f"Articles saved to: {output_file}")
        return True
    else:
        print("No articles found!")
        return False

if __name__ == "__main__":
    test_scraper_direct()

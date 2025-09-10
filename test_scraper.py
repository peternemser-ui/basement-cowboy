#!/usr/bin/env python3
"""
Simple test script to debug the scraper
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def test_single_site():
    """Test scraping a single site with detailed output"""
    url = "https://abcnews.go.com"
    
    print(f"Testing: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print("Making request...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Parsing HTML...")
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            print(f"Found {len(links)} total links")
            
            articles = []
            for i, link in enumerate(links[:20]):  # Test first 20 links
                headline = link.get_text(strip=True)
                href = link['href']
                
                if headline and len(headline) >= 10:
                    # Make absolute URL
                    if not href.startswith(('http://', 'https://')):
                        from urllib.parse import urljoin
                        href = urljoin(url, href)
                    
                    articles.append({
                        "headline": headline,
                        "link": href,
                        "summary": headline[:100] + "..." if len(headline) > 100 else headline
                    })
                    
                    print(f"Article {i+1}: {headline[:60]}...")
            
            print(f"\nTotal valid articles found: {len(articles)}")
            
            if articles:
                # Save test output
                output_file = f"test_articles_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)
                print(f"Saved to: {output_file}")
                
                return True
            else:
                print("No articles found!")
                return False
        else:
            print(f"Failed to fetch page: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_single_site()

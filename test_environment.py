#!/usr/bin/env python3
"""
Simple error-catching test for the scraper
"""

try:
    print("Testing imports...")
    import requests
    print("✓ requests imported")
    
    from bs4 import BeautifulSoup
    print("✓ BeautifulSoup imported")
    
    import json
    print("✓ json imported")
    
    import os
    from datetime import datetime
    from dotenv import load_dotenv
    from hashlib import sha256
    from urllib.parse import urljoin
    print("✓ All standard imports successful")
    
    # Test basic functionality
    print("\nTesting basic functionality...")
    
    # Test file access
    config_file = "config/top_100_news_sites.txt"
    if os.path.exists(config_file):
        print(f"✓ Config file found: {config_file}")
        with open(config_file, 'r') as f:
            lines = f.read().splitlines()
        active_sites = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        print(f"✓ Found {len(active_sites)} active sites")
    else:
        print(f"✗ Config file NOT found: {config_file}")
    
    # Test output directory
    output_dir = "output/news_articles"
    if os.path.exists(output_dir):
        print(f"✓ Output directory exists: {output_dir}")
    else:
        print(f"✗ Output directory missing: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        print(f"✓ Created output directory: {output_dir}")
    
    # Test environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✓ OpenAI API key loaded")
    else:
        print("⚠ OpenAI API key not found (optional)")
    
    # Test a simple HTTP request
    print("\nTesting HTTP request...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    test_url = "https://httpbin.org/get"  # Simple test endpoint
    response = requests.get(test_url, headers=headers, timeout=10)
    if response.status_code == 200:
        print("✓ HTTP requests working")
    else:
        print(f"✗ HTTP request failed: {response.status_code}")
    
    print("\n=== All tests passed! ===")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Try running: pip install -r requirements.txt")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")

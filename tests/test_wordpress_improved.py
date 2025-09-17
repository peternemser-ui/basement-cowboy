#!/usr/bin/env python3
"""
Updated WordPress Connection Test with Better Headers
"""

import json
import requests
from base64 import b64encode

def test_wordpress_connection_improved():
    """Test WordPress REST API with browser-like headers."""
    print("🔍 Testing WordPress Connection (Improved)")
    print("=" * 45)
    
    # Load config
    with open('config/wordpress_config.json', 'r') as f:
        config = json.load(f)
    
    wp_url = config['wordpress_url']
    username = config['username'] 
    app_password = config['application_password']
    
    # Use browser-like headers
    headers = {
        "Authorization": f"Basic {b64encode(f'{username}:{app_password}'.encode()).decode()}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print(f"🌐 Testing: {wp_url}")
    print(f"👤 User: {username}")
    
    # Test 1: Create a test post
    print("\n1. Testing post creation...")
    try:
        post_data = {
            "title": "Python Test - Can Delete",
            "content": "This is a test post from Python. You can safely delete this.",
            "status": "draft"
        }
        
        response = requests.post(
            f"{wp_url}/wp-json/wp/v2/posts",
            json=post_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            post_info = response.json()
            print("✅ Post creation successful!")
            print(f"   Created draft post ID: {post_info.get('id')}")
            print(f"   Title: {post_info.get('title', {}).get('rendered', 'N/A')}")
            return True
        else:
            print(f"❌ Post creation failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if test_wordpress_connection_improved():
        print("\n🎉 WordPress is working perfectly with Python!")
        print("The issue was likely the User-Agent or request headers.")
        print("Your app should now work for publishing!")
    else:
        print("\n❌ Still having issues. Let's debug further.")
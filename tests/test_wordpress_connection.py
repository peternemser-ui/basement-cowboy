#!/usr/bin/env python3
"""
Quick WordPress Connection Test
Tests the WordPress REST API connection and credentials.
"""

import json
import requests
from base64 import b64encode

def test_wordpress_connection():
    """Test WordPress REST API connection."""
    print("🔍 Testing WordPress Connection")
    print("=" * 40)
    
    # Load config
    try:
        with open('config/wordpress_config.json', 'r') as f:
            config = json.load(f)
        print("✅ Config loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    wp_url = config['wordpress_url']
    username = config['username'] 
    app_password = config['application_password']
    
    print(f"🌐 Testing: {wp_url}")
    print(f"👤 User: {username}")
    
    # Test 1: Basic site accessibility
    print("\n1. Testing site accessibility...")
    try:
        response = requests.get(wp_url, timeout=10)
        if response.status_code == 200:
            print("✅ Site is accessible")
        else:
            print(f"⚠️  Site returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Site not accessible: {e}")
        return False
    
    # Test 2: REST API endpoint
    print("\n2. Testing REST API endpoint...")
    try:
        api_url = f"{wp_url}/wp-json/wp/v2/"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            print("✅ REST API endpoint accessible")
        else:
            print(f"❌ REST API returned status {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ REST API error: {e}")
        return False
    
    # Test 3: Authentication
    print("\n3. Testing authentication...")
    try:
        auth_header = b64encode(f'{username}:{app_password}'.encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        # Test with a simple GET request to posts
        test_url = f"{wp_url}/wp-json/wp/v2/posts?per_page=1"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Authentication successful")
            posts = response.json()
            print(f"   Found {len(posts)} post(s)")
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid credentials")
            print("   Check your username and application password")
            return False
        elif response.status_code == 403:
            print("❌ Authentication failed - Permission denied")
            print("   User may not have publishing permissions")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    # Test 4: Try creating a draft post
    print("\n4. Testing post creation...")
    try:
        post_data = {
            "title": "Test Post - Can be deleted",
            "content": "This is a test post created by Basement Cowboy. You can safely delete this.",
            "status": "draft"  # Create as draft only
        }
        
        create_url = f"{wp_url}/wp-json/wp/v2/posts"
        response = requests.post(create_url, json=post_data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            post_info = response.json()
            print("✅ Post creation successful")
            print(f"   Created draft post ID: {post_info.get('id')}")
            print(f"   Title: {post_info.get('title', {}).get('rendered', 'N/A')}")
            return True
        else:
            print(f"❌ Post creation failed: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False
            
    except Exception as e:
        print(f"❌ Post creation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 WordPress Connection Diagnostics")
    print("===================================")
    
    if test_wordpress_connection():
        print("\n🎉 All tests passed! WordPress is configured correctly.")
        print("\nYour WordPress setup is working. The publish error might be:")
        print("1. A temporary network issue")
        print("2. WordPress server overload") 
        print("3. A specific error in the app code")
        print("\nTry publishing again, and if it fails, check the Flask console for detailed error messages.")
    else:
        print("\n❌ WordPress configuration needs attention.")
        print("\nTo fix:")
        print("1. Verify your WordPress site is online")
        print("2. Check your username in wordpress_config.json") 
        print("3. Regenerate your Application Password:")
        print("   - Go to WordPress Admin → Users → Profile")
        print("   - Scroll to 'Application Passwords'")
        print("   - Create new password and update config file")
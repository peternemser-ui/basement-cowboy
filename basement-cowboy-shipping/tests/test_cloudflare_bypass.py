#!/usr/bin/env python3
"""
Test script to check if we can bypass Cloudflare protection for WordPress API
"""

import requests
import json
import time
from base64 import b64encode

# WordPress config
WP_SITE = "https://basementcowboy.com"
WP_USER = "thebasementcow"
WP_APP_PASSWORD = "LgTw Bd3y UcJy aOZR q9Zr Nd9r"  # From config file

def test_cloudflare_bypass():
    """Test different methods to bypass Cloudflare"""
    
    print("🔬 Testing Cloudflare bypass methods...")
    
    # Enhanced headers to mimic a real browser
    headers = {
        "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://basementcowboy.com",
        "Referer": "https://basementcowboy.com/wp-admin/"
    }
    
    # Create session for cookie persistence
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        print("📍 Step 1: Warming up with main site...")
        warmup_response = session.get(f"{WP_SITE}/", timeout=30)
        print(f"   Warmup status: {warmup_response.status_code}")
        print(f"   Cookies received: {len(session.cookies)}")
        
        # Check if Cloudflare challenged us
        if "Just a moment" in warmup_response.text or "cf-chl" in warmup_response.text:
            print("   ⚠️  Cloudflare challenge detected on main site")
        else:
            print("   ✅ Main site accessible")
        
        print("\n📍 Step 2: Waiting 3 seconds...")
        time.sleep(3)
        
        print("📍 Step 3: Testing API endpoint...")
        api_url = f"{WP_SITE}/wp-json/wp/v2/posts"
        
        # Try a simple GET first to see if API is accessible
        get_response = session.get(api_url + "?per_page=1", timeout=30)
        print(f"   GET request status: {get_response.status_code}")
        
        if get_response.status_code == 403 and "Just a moment" in get_response.text:
            print("   ❌ Cloudflare is still blocking API requests")
            print("   📝 Response preview:", get_response.text[:200])
            return False
        elif get_response.status_code == 200:
            print("   ✅ API GET request successful")
        else:
            print(f"   ⚠️  API GET request returned: {get_response.status_code}")
        
        print("\n📍 Step 4: Testing POST to API...")
        # Simple test post data
        test_post = {
            "title": "API Test Post",
            "content": "This is a test post to verify API connectivity.",
            "status": "draft"  # Use draft to avoid publishing test content
        }
        
        post_response = session.post(api_url, json=test_post, timeout=60)
        print(f"   POST request status: {post_response.status_code}")
        
        if post_response.status_code == 403:
            print("   ❌ Cloudflare is blocking POST requests")
            if "Just a moment" in post_response.text:
                print("   📝 Cloudflare challenge page detected")
            return False
        elif post_response.status_code == 201:
            print("   ✅ POST request successful - API is working!")
            response_data = post_response.json()
            print(f"   📝 Created draft post ID: {response_data.get('id')}")
            return True
        else:
            print(f"   ⚠️  POST request failed with: {post_response.status_code}")
            print(f"   📝 Response: {post_response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def alternative_bypass_test():
    """Try a different approach"""
    print("\n🔬 Testing alternative bypass method...")
    
    # Try with minimal headers first
    minimal_headers = {
        "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
        "Content-Type": "application/json",
        "User-Agent": "WordPress/6.0; https://basementcowboy.com"
    }
    
    try:
        print("📍 Testing with WordPress-style User-Agent...")
        response = requests.get(f"{WP_SITE}/wp-json/wp/v2/posts?per_page=1", 
                              headers=minimal_headers, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ WordPress-style User-Agent works!")
            return True
        elif "Just a moment" in response.text:
            print("   ❌ Still blocked by Cloudflare")
            return False
        else:
            print(f"   ⚠️  Other error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Cloudflare bypass tests...\n")
    
    # Test main method
    success1 = test_cloudflare_bypass()
    
    # Test alternative method
    success2 = alternative_bypass_test()
    
    print(f"\n📊 Results:")
    print(f"   Enhanced browser method: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"   WordPress User-Agent method: {'✅ Success' if success2 else '❌ Failed'}")
    
    if success1 or success2:
        print("\n🎉 At least one method works! The app should be able to publish.")
    else:
        print("\n😞 Both methods failed. May need additional Cloudflare bypass techniques.")
    
    print("\n🔧 Next steps:")
    if not (success1 or success2):
        print("   1. Check if Cloudflare settings can be adjusted")
        print("   2. Consider using Cloudflare API tokens")
        print("   3. Look into WordPress plugin alternatives")
    else:
        print("   1. Test the publishing function in the app")
        print("   2. Monitor for any rate limiting issues")
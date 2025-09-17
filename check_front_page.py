#!/usr/bin/env python3
"""
WordPress Front Page Diagnostic Tool
Checks why posts aren't showing on the front page
"""

import requests
import json
from datetime import datetime
import base64

def load_wp_config():
    """Load WordPress configuration"""
    try:
        with open('config/wordpress_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading WordPress config: {e}")
        return None

def check_wp_settings(config):
    """Check WordPress front page settings"""
    print("🔍 Checking WordPress Front Page Settings")
    print("=" * 60)
    
    # Create auth header
    auth_string = f"{config['username']}:{config['application_password']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Check front page settings
        settings_url = f"{config['wordpress_url']}/wp-json/wp/v2/settings"
        response = requests.get(settings_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            settings = response.json()
            
            print(f"📄 Front Page Shows: {settings.get('show_on_front', 'posts')}")
            if settings.get('show_on_front') == 'page':
                print(f"📌 Static Front Page ID: {settings.get('page_on_front', 'Not set')}")
                print(f"📝 Posts Page ID: {settings.get('page_for_posts', 'Not set')}")
            
            print(f"📰 Posts Per Page: {settings.get('posts_per_page', 'Unknown')}")
            print(f"🏠 Site Title: {settings.get('title', 'Unknown')}")
            print(f"📝 Site Description: {settings.get('description', 'Unknown')}")
            
        else:
            print(f"❌ Failed to get settings: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking settings: {e}")

def check_latest_posts(config):
    """Check latest posts and their status"""
    print("\n🔍 Checking Latest Posts")
    print("=" * 60)
    
    # Create auth header
    auth_string = f"{config['username']}:{config['application_password']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get latest posts
        posts_url = f"{config['wordpress_url']}/wp-json/wp/v2/posts?per_page=5&_fields=id,title,slug,status,date,sticky,link"
        response = requests.get(posts_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            posts = response.json()
            
            for i, post in enumerate(posts, 1):
                status_emoji = "✅" if post['status'] == 'publish' else "⚠️"
                sticky_emoji = "📌" if post.get('sticky', False) else "📄"
                
                print(f"{i}. {sticky_emoji} {status_emoji} {post['title']['rendered']}")
                print(f"   🔗 {post['link']}")
                print(f"   📅 {post['date']}")
                print(f"   📊 Status: {post['status']}")
                if post.get('sticky', False):
                    print(f"   ⭐ STICKY POST")
                print()
                
        else:
            print(f"❌ Failed to get posts: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking posts: {e}")

def check_front_page_content(config):
    """Check what's actually on the front page"""
    print("🔍 Checking Front Page Content")
    print("=" * 60)
    
    try:
        # Get front page content
        response = requests.get(config['wordpress_url'], timeout=30)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for our recent posts
            if "Daily News Roundup" in content:
                print("✅ 'Daily News Roundup' found on front page")
            else:
                print("❌ 'Daily News Roundup' NOT found on front page")
                
            if "basementcowboy.com/wp-content/uploads/2025/09/" in content:
                print("✅ Recent images found on front page")
            else:
                print("❌ Recent images NOT found on front page")
                
            # Check for common WordPress elements
            if "wp-content" in content:
                print("✅ WordPress content detected")
            else:
                print("❌ No WordPress content detected")
                
            print(f"📏 Front page content length: {len(content)} characters")
            
        else:
            print(f"❌ Failed to load front page: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking front page: {e}")

def main():
    print("🏠 WordPress Front Page Diagnostic Tool")
    print("=" * 60)
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load WordPress config
    config = load_wp_config()
    if not config:
        return
        
    print(f"🌐 WordPress Site: {config['wordpress_url']}")
    print(f"👤 User: {config['username']}")
    print()
    
    # Run diagnostics
    check_wp_settings(config)
    check_latest_posts(config)
    check_front_page_content(config)
    
    print("\n💡 Recommendations:")
    print("1. If 'show_on_front' is 'page', you need to set it to 'posts'")
    print("2. Check if your latest post is actually published (not draft)")
    print("3. Clear any caching plugins on your WordPress site")
    print("4. Check your theme's front page template")
    print("5. Make sure your post is set to 'sticky' if you want it featured")

if __name__ == "__main__":
    main()
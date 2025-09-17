#!/usr/bin/env python3
"""
WordPress Front Page Fix Tool
Attempts to fix common front page display issues
"""

import requests
import json
import base64
from datetime import datetime

def load_wp_config():
    """Load WordPress configuration"""
    try:
        with open('config/wordpress_config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading WordPress config: {e}")
        return None

def fix_front_page_settings(config):
    """Fix WordPress front page to show latest posts"""
    print("🔧 Attempting to fix front page settings...")
    
    # Create auth header
    auth_string = f"{config['username']}:{config['application_password']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Update front page settings to show posts
        settings_url = f"{config['wordpress_url']}/wp-json/wp/v2/settings"
        settings_data = {
            'show_on_front': 'posts'  # Show latest posts on front page
        }
        
        response = requests.post(settings_url, 
                               headers=headers, 
                               json=settings_data, 
                               timeout=30)
        
        if response.status_code == 200:
            print("✅ Front page settings updated successfully!")
            print("📄 Front page now shows latest posts")
            return True
        else:
            print(f"❌ Failed to update settings: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating settings: {e}")
        return False

def make_latest_post_sticky(config):
    """Make the latest post sticky (featured)"""
    print("📌 Making latest post sticky...")
    
    # Create auth header
    auth_string = f"{config['username']}:{config['application_password']}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get latest post
        posts_url = f"{config['wordpress_url']}/wp-json/wp/v2/posts?per_page=1"
        response = requests.get(posts_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            posts = response.json()
            if posts:
                latest_post = posts[0]
                post_id = latest_post['id']
                
                # Make it sticky
                update_url = f"{config['wordpress_url']}/wp-json/wp/v2/posts/{post_id}"
                update_data = {
                    'sticky': True,
                    'status': 'publish'  # Ensure it's published
                }
                
                update_response = requests.post(update_url, 
                                              headers=headers, 
                                              json=update_data, 
                                              timeout=30)
                
                if update_response.status_code == 200:
                    print(f"✅ Post '{latest_post['title']['rendered']}' is now sticky!")
                    print(f"🔗 {latest_post['link']}")
                    return True
                else:
                    print(f"❌ Failed to make post sticky: {update_response.status_code}")
                    return False
            else:
                print("❌ No posts found")
                return False
        else:
            print(f"❌ Failed to get posts: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error making post sticky: {e}")
        return False

def clear_cache_notice():
    """Display cache clearing instructions"""
    print("\n🧹 Cache Clearing Instructions:")
    print("=" * 50)
    print("1. 🌐 Cloudflare (if using):")
    print("   - Go to Cloudflare Dashboard")
    print("   - Caching → Purge Everything")
    print()
    print("2. 🔌 WordPress Caching Plugins:")
    print("   - WP Rocket: Settings → Clear Cache")
    print("   - W3 Total Cache: Performance → Purge All Caches")
    print("   - WP Super Cache: Settings → Delete Cache")
    print()
    print("3. 🌐 Browser Cache:")
    print("   - Press Ctrl+F5 or Cmd+Shift+R")
    print("   - Try incognito/private browsing mode")

def main():
    print("🏠 WordPress Front Page Fix Tool")
    print("=" * 50)
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load WordPress config
    config = load_wp_config()
    if not config:
        return
        
    print(f"🌐 WordPress Site: {config['wordpress_url']}")
    print(f"👤 User: {config['username']}")
    print()
    
    # Try to fix the issues
    print("🔧 Attempting to fix front page issues...")
    print()
    
    success1 = fix_front_page_settings(config)
    success2 = make_latest_post_sticky(config)
    
    if success1 or success2:
        print("\n🎉 Some fixes were applied successfully!")
    else:
        print("\n⚠️ Unable to apply automatic fixes due to API restrictions")
        print("This is likely due to Cloudflare security settings")
    
    clear_cache_notice()
    
    print(f"\n🔗 Check your site: {config['wordpress_url']}")
    print("🎯 Your latest post should now appear on the front page!")

if __name__ == "__main__":
    main()

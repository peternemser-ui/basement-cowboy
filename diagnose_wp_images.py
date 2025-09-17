#!/usr/bin/env python3
"""
Diagnose why images aren't showing on WordPress and provide solutions
"""

import json
import requests
from base64 import b64encode
import re

# Load WordPress config
with open('config/wordpress_config.json', 'r') as f:
    wp_config = json.load(f)

WP_SITE = wp_config['wordpress_url']
WP_USER = wp_config['username']
WP_APP_PASSWORD = wp_config['application_password']

def check_latest_post():
    """Check the latest post and diagnose image issues"""
    try:
        headers = {
            "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
            "User-Agent": "Mozilla/5.0"
        }
        
        # Get latest post
        response = requests.get(f"{WP_SITE}/wp-json/wp/v2/posts?per_page=1", headers=headers)
        
        if response.status_code == 200:
            posts = response.json()
            if posts:
                post = posts[0]
                print(f"📰 Latest Post: {post.get('title', {}).get('rendered', 'No title')}")
                print(f"🔗 URL: {post.get('link')}")
                print(f"📅 Date: {post.get('date')}")
                print("=" * 60)
                
                # Analyze content
                content = post.get('content', {}).get('rendered', '')
                
                # Check for our CSS classes
                if 'bc-news-container' in content:
                    print("✅ New CSS container found")
                else:
                    print("❌ CSS container missing - using old format")
                
                # Count images
                img_tags = re.findall(r'<img[^>]*>', content)
                img_count = len(img_tags)
                print(f"📷 Total images in HTML: {img_count}")
                
                if img_count > 0:
                    print("\n🖼️  Image Analysis:")
                    for i, img_tag in enumerate(img_tags[:3]):
                        print(f"   Image {i+1}: {img_tag[:100]}...")
                        
                        # Extract src
                        src_match = re.search(r'src=["\']([^"\']*)["\']', img_tag)
                        if src_match:
                            img_url = src_match.group(1)
                            
                            # Test accessibility
                            try:
                                img_response = requests.head(img_url, timeout=5)
                                if img_response.status_code == 200:
                                    print(f"      ✅ Accessible ({img_response.status_code})")
                                else:
                                    print(f"      ❌ Not accessible ({img_response.status_code})")
                            except:
                                print(f"      ❌ Failed to test URL")
                
                # Check for structural issues
                print(f"\n🔍 Content Structure Analysis:")
                print(f"   Total content length: {len(content):,} characters")
                
                # Check for common WordPress theme issues
                if '<style>' in content:
                    print("   ✅ Contains embedded CSS")
                else:
                    print("   ❌ No embedded CSS found")
                
                if 'bc-news-article' in content:
                    print("   ✅ Contains article containers")
                else:
                    print("   ❌ Missing article containers")
                
                # Check what's actually being displayed
                visible_content = content.replace('<style>', '').split('</style>')[-1] if '</style>' in content else content
                
                # Count actual article sections
                article_sections = visible_content.count('bc-news-article')
                print(f"   📝 Article sections: {article_sections}")
                
                # Show content sample
                print(f"\n📝 Content Preview (first 300 chars):")
                clean_preview = re.sub(r'<[^>]+>', '', visible_content[:300])
                print(f"   {clean_preview}...")
                
                return post
            else:
                print("❌ No posts found")
                return None
        else:
            print(f"❌ Failed to get posts: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_image_urls():
    """Test specific image URLs that should be working"""
    test_urls = [
        "https://basementcowboy.com/wp-content/uploads/2025/09/openai_image-13.png",
        "https://basementcowboy.com/wp-content/uploads/2025/09/openai_image-14.png"
    ]
    
    print(f"\n🧪 Testing Known Image URLs:")
    for url in test_urls:
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {url} - Accessible")
            else:
                print(f"   ❌ {url} - Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} - Error: {e}")

def suggest_solutions():
    """Provide troubleshooting suggestions"""
    print(f"\n💡 Troubleshooting Suggestions:")
    print(f"1. 🎨 Theme Issues:")
    print(f"   - Your theme might be stripping out CSS or custom HTML")
    print(f"   - Try switching to a default WordPress theme (Twenty Twenty-Four)")
    print(f"   - Check if theme has content filters or sanitization")
    
    print(f"\n2. 🔧 Plugin Conflicts:")
    print(f"   - Security plugins might be blocking custom CSS")
    print(f"   - Cache plugins might be serving old content")
    print(f"   - Deactivate plugins temporarily to test")
    
    print(f"\n3. 🛡️ WordPress Security:")
    print(f"   - WordPress might be sanitizing HTML content")
    print(f"   - Check if user has 'unfiltered_html' capability")
    print(f"   - Try publishing as Administrator role")
    
    print(f"\n4. 🌐 Browser/CDN Issues:")
    print(f"   - Clear browser cache and check")
    print(f"   - Disable any CDN temporarily")
    print(f"   - Check in incognito/private browsing mode")
    
    print(f"\n5. 📱 Alternative Approach:")
    print(f"   - Create a custom WordPress page template")
    print(f"   - Use WordPress blocks instead of raw HTML")
    print(f"   - Set featured images for posts")

if __name__ == "__main__":
    print("🔍 WordPress Image Display Diagnostic Tool")
    print("=" * 60)
    
    post = check_latest_post()
    test_image_urls()
    suggest_solutions()
    
    if post:
        print(f"\n🎯 Next Steps:")
        print(f"1. Publish a new article with the updated code")
        print(f"2. Check {post.get('link')} to see if images appear")
        print(f"3. If still not working, try the troubleshooting suggestions above")
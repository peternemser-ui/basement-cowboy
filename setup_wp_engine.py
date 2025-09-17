#!/usr/bin/env python3
"""
Quick setup script for WP Engine WordPress sites
"""

import json
import os
from pathlib import Path

def setup_wp_engine():
    print("🚀 WP Engine WordPress Setup for Basement Cowboy")
    print("=" * 60)
    
    config_dir = Path(__file__).parent / 'config'
    config_dir.mkdir(exist_ok=True)
    
    print("\n📝 Please provide your WP Engine site details:")
    print("(You can find these in your WP Engine dashboard)")
    
    # Get site information
    site_url = input("\n1. Enter your WP Engine site URL (e.g., https://yoursite.wpengine.com): ").strip()
    if not site_url.startswith('http'):
        site_url = f"https://{site_url}"
    site_url = site_url.rstrip('/')
    
    username = input("2. Enter your WordPress username: ").strip()
    
    print("\n3. Application Password Setup:")
    print("   - Log into your WordPress admin dashboard")
    print("   - Go to Users → Your Profile")
    print("   - Scroll down to 'Application Passwords'")
    print("   - Enter name: 'Basement Cowboy API'")
    print("   - Click 'Add New Application Password'")
    print("   - Copy the generated password (format: xxxx xxxx xxxx xxxx)")
    
    app_password = input("\n   Enter your Application Password: ").strip()
    
    # Determine environment
    environment = "production"
    if "staging" in site_url.lower():
        environment = "staging"
    elif "dev" in site_url.lower():
        environment = "development"
    
    # Create configuration
    config = {
        "wordpress_url": site_url,
        "username": username,
        "application_password": app_password,
        "environment": environment,
        "hosting_provider": "WP Engine",
        "setup_date": str(Path(__file__).stat().st_mtime)
    }
    
    # Save configuration
    config_file = config_dir / 'wordpress_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to: {config_file}")
    
    # Test the connection
    print("\n🧪 Testing WordPress connection...")
    try:
        import requests
        from base64 import b64encode
        
        headers = {
            "Authorization": f"Basic {b64encode(f'{username}:{app_password}'.encode()).decode()}",
            "User-Agent": "Basement-Cowboy/1.0",
            "Cache-Control": "no-cache"
        }
        
        test_url = f"{site_url}/wp-json/wp/v2/posts?per_page=1"
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ WordPress API connection successful!")
            print(f"   Site: {site_url}")
            print(f"   Environment: {environment}")
            print(f"   User: {username}")
            
            # Test media upload capability
            media_url = f"{site_url}/wp-json/wp/v2/media"
            media_response = requests.get(media_url, headers=headers, timeout=5)
            
            if media_response.status_code == 200:
                print("✅ Media upload capability confirmed")
            else:
                print("⚠️  Media upload may need additional permissions")
                
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            print("\n🔧 Troubleshooting:")
            print("   - Verify your application password is correct")
            print("   - Check that WordPress REST API is enabled")
            print("   - Ensure your user has appropriate permissions")
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Check your internet connection")
        print("   - Verify the site URL is correct")
        print("   - Ensure the site is accessible")
    
    print("\n🎯 Next Steps:")
    print("1. Start your Basement Cowboy application: python run.py")
    print("2. Visit http://127.0.0.1:5000 to test the interface")
    print("3. Generate articles and publish to your WP Engine site")
    
    print(f"\n📁 Configuration file location: {config_file}")
    print("💡 You can edit this file later to change settings")

if __name__ == "__main__":
    setup_wp_engine()
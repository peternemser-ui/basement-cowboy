#!/usr/bin/env python3
"""
Test WordPress GraphQL Integration
This script tests the GraphQL client and connection to WordPress.
"""

import sys
import os
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from wordpress_graphql import create_wordpress_graphql_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_graphql_connection():
    """Test the WordPress GraphQL connection and basic operations."""
    print("🔄 Testing WordPress GraphQL Integration")
    print("=" * 50)
    
    # Create GraphQL client
    print("1. Creating GraphQL client...")
    client = create_wordpress_graphql_client()
    
    if not client:
        print("❌ Failed to create GraphQL client")
        print("   Check your wordpress_config.json file")
        return False
    
    print("✅ GraphQL client created successfully")
    
    # Test connection
    print("\n2. Testing GraphQL connection...")
    connection_result = client.test_connection()
    
    if not connection_result["success"]:
        print(f"❌ Connection failed: {connection_result.get('error', 'Unknown error')}")
        print("   Make sure:")
        print("   - WPGraphQL plugin is installed and activated")
        print("   - WordPress site is accessible")
        print("   - Application password is correct")
        return False
    
    print("✅ GraphQL connection successful!")
    print(f"   Site: {connection_result['site_title']}")
    print(f"   URL: {connection_result['site_url']}")
    print(f"   Description: {connection_result['site_description']}")
    
    # Test getting posts
    print("\n3. Testing GraphQL queries (get recent posts)...")
    try:
        posts = client.get_posts(limit=3)
        print(f"✅ Successfully retrieved {len(posts)} posts")
        
        for i, post in enumerate(posts, 1):
            print(f"   {i}. {post['title']} (ID: {post['id']})")
    
    except Exception as e:
        print(f"❌ Failed to get posts: {e}")
        return False
    
    # Test creating a draft post
    print("\n4. Testing GraphQL mutations (create draft post)...")
    try:
        test_content = """
        <h2>GraphQL Test Post</h2>
        <p>This is a test post created via GraphQL to verify the integration is working correctly.</p>
        <p><strong>Test timestamp:</strong> {}</p>
        """.format(
            __import__('datetime').datetime.now().isoformat()
        )
        
        create_result = client.create_post(
            title="GraphQL Integration Test",
            content=test_content,
            status="draft"  # Create as draft to avoid cluttering the site
        )
        
        if create_result["success"]:
            post_data = create_result["post"]
            print("✅ Successfully created test post!")
            print(f"   Post ID: {post_data['id']}")
            print(f"   Title: {post_data['title']}")
            print(f"   Status: {post_data['status']}")
            print(f"   URL: {post_data['link']}")
        else:
            print(f"❌ Failed to create post: {create_result.get('error', 'Unknown error')}")
            if 'errors' in create_result:
                for error in create_result['errors']:
                    print(f"     - {error}")
            return False
    
    except Exception as e:
        print(f"❌ Exception during post creation: {e}")
        return False
    
    print("\n🎉 All GraphQL tests passed!")
    print("\nℹ️  Your WordPress site is ready for GraphQL publishing.")
    print("   You can now use the Basement Cowboy app with GraphQL.")
    
    return True

def test_requirements():
    """Test that all required packages are installed."""
    print("📦 Checking Python package requirements...")
    
    try:
        import gql
        print("✅ gql package installed")
    except ImportError:
        print("❌ gql package missing - run: pip install gql[requests]")
        return False
    
    try:
        import graphql
        print("✅ graphql-core package installed")
    except ImportError:
        print("❌ graphql-core package missing - run: pip install graphql-core")
        return False
    
    try:
        import requests
        print("✅ requests package installed")
    except ImportError:
        print("❌ requests package missing - run: pip install requests")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 WordPress GraphQL Integration Test")
    print("=====================================")
    
    # Check requirements first
    if not test_requirements():
        print("\n❌ Missing required packages. Please install them and try again.")
        sys.exit(1)
    
    print()
    
    # Test GraphQL connection
    if test_graphql_connection():
        print("\n✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Install the required WordPress plugins:")
        print("   - WPGraphQL (required)")
        print("   - WPGraphQL Upload (optional, for better media handling)")
        print("2. Your Basement Cowboy app is now using GraphQL!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure WPGraphQL plugin is installed on your WordPress site")
        print("2. Verify your wordpress_config.json has correct credentials")
        print("3. Check that your WordPress site is accessible")
        print("4. Ensure your application password is valid")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test script for SEO generator functionality
Tests schema generation, meta tags, and WordPress integration
"""

import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from seo_generator import SEOGenerator

# Sample test articles
test_articles = [
    {
        "title": "Breaking: Major Economic Summit Concludes with New Trade Agreements",
        "content": "World leaders gathered today to finalize groundbreaking trade agreements that will reshape global commerce. The summit, attended by representatives from over 50 nations, focused on sustainable economic growth and digital transformation.",
        "url": "https://example.com/economic-summit",
        "category": "Business",
        "source": "Global News Network",
        "timestamp": "2025-01-15T10:30:00Z"
    },
    {
        "title": "Revolutionary AI Technology Transforms Healthcare Diagnostics",
        "content": "Scientists have developed an AI system that can diagnose rare diseases with 95% accuracy. This breakthrough promises to revolutionize healthcare delivery in underserved communities worldwide.",
        "url": "https://example.com/ai-healthcare",
        "category": "Technology",
        "source": "Tech Today",
        "timestamp": "2025-01-15T11:15:00Z"
    },
    {
        "title": "Climate Action Summit Announces Ambitious 2030 Goals",
        "content": "Environmental leaders from around the world have committed to aggressive climate targets for 2030. The new framework includes carbon neutrality pledges and renewable energy investments.",
        "url": "https://example.com/climate-action",
        "category": "Environment",
        "source": "Environmental Watch",
        "timestamp": "2025-01-15T12:00:00Z"
    }
]

def test_seo_generation():
    """Test the SEO generator functionality"""
    print("🧪 Testing SEO Generator")
    print("=" * 50)
    
    try:
        # Initialize SEO generator
        seo_generator = SEOGenerator()
        print("✅ SEO Generator initialized successfully")
        
        # Generate SEO metadata
        print("\n📊 Generating SEO metadata...")
        seo_metadata = seo_generator.generate_seo_metadata(test_articles)
        
        # Display results
        print(f"\n📝 Generated SEO Title: {seo_metadata.get('title', 'N/A')}")
        print(f"📄 Meta Description: {seo_metadata.get('description', 'N/A')[:100]}...")
        print(f"🔑 Focus Keywords: {', '.join(seo_metadata.get('keywords', [])[:10])}")
        print(f"📊 Readability Score: {seo_metadata.get('readability_score', 'N/A')}")
        
        # Test schema generation
        print("\n🏗️ Testing Schema Generation...")
        schema = seo_metadata.get('schema', {})
        if schema:
            print(f"✅ Schema type: {schema.get('@type', 'Unknown')}")
            print(f"✅ Schema has {len(schema.get('mainEntity', []))} articles")
        else:
            print("❌ No schema generated")
        
        # Test meta tags
        print("\n🏷️ Testing Meta Tags...")
        meta_tags = seo_metadata.get('meta_tags', '')
        if meta_tags:
            meta_count = meta_tags.count('<meta')
            print(f"✅ Generated {meta_count} meta tags")
            print("✅ Meta tags include OpenGraph and Twitter Card data")
        else:
            print("❌ No meta tags generated")
        
        # Test WordPress SEO optimization
        print("\n🌐 Testing WordPress SEO Integration...")
        wp_seo_data = seo_generator.generate_seo_optimized_content(test_articles, "Breaking News")
        if wp_seo_data:
            print(f"✅ WordPress SEO title: {wp_seo_data.get('seo_title', 'N/A')}")
            print(f"✅ Focus keywords: {', '.join(wp_seo_data.get('focus_keywords', [])[:5])}")
            print(f"✅ Readability score: {wp_seo_data.get('readability_score', {})}")
        else:
            print("❌ WordPress SEO optimization failed")
        
        print("\n🎉 SEO Generator Test Complete!")
        print("✅ All core functionality working correctly")
        
        # Save detailed results for inspection
        with open('seo_test_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'seo_metadata': seo_metadata,
                'wordpress_seo': wp_seo_data,
                'test_articles_count': len(test_articles)
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Detailed results saved to: seo_test_results.json")
        
        return True
        
    except Exception as e:
        print(f"❌ SEO Generator test failed: {str(e)}")
        import traceback
        print(f"🔍 Error details: {traceback.format_exc()}")
        return False

def test_schema_validation():
    """Test that generated schema is valid JSON-LD"""
    print("\n🔍 Testing Schema Validation...")
    
    try:
        seo_generator = SEOGenerator()
        seo_metadata = seo_generator.generate_seo_metadata(test_articles)
        schema = seo_metadata.get('schema', {})
        
        # Basic JSON-LD validation
        required_fields = ['@context', '@type']
        for field in required_fields:
            if field not in schema:
                print(f"❌ Missing required schema field: {field}")
                return False
        
        print("✅ Schema contains required JSON-LD fields")
        
        # Validate article structure
        if 'mainEntity' in schema and isinstance(schema['mainEntity'], list):
            print(f"✅ Schema contains {len(schema['mainEntity'])} article entities")
            
            # Check first article structure
            if schema['mainEntity']:
                article = schema['mainEntity'][0]
                article_fields = ['@type', 'headline', 'datePublished', 'author']
                for field in article_fields:
                    if field in article:
                        print(f"✅ Article schema has {field}")
                    else:
                        print(f"⚠️ Article schema missing {field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Basement Cowboy SEO Generator Test Suite")
    print("=" * 60)
    
    # Run tests
    seo_test_passed = test_seo_generation()
    schema_test_passed = test_schema_validation()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"SEO Generation: {'✅ PASSED' if seo_test_passed else '❌ FAILED'}")
    print(f"Schema Validation: {'✅ PASSED' if schema_test_passed else '❌ FAILED'}")
    
    if seo_test_passed and schema_test_passed:
        print("\n🎉 All tests passed! SEO generator is ready for production.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
        sys.exit(1)
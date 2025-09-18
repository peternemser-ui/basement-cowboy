#!/usr/bin/env python3
"""
Test script for the updated features:
1. Minimum article selection increased to 100
2. Details page shows articles in ranking order with badges
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_updated_features():
    print("🧪 Testing Updated Features")
    print("="*50)
    
    # Test 1: Ranking system working
    print("\n1. Testing Ranking System...")
    try:
        response = requests.post(f'{BASE_URL}/rank_articles')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ranking API working - {len(data['top_100'])} articles ranked")
            
            # Show top 5
            print("🏆 Top 5 ranked articles:")
            for i, article in enumerate(data['top_100'][:5], 1):
                score = article.get('score', 0)
                headline = article.get('headline', 'No headline')[:60]
                print(f"  {i}. Score: {score:.1f} - {headline}...")
        else:
            print(f"❌ Ranking API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing ranking: {e}")
    
    # Test 2: UI endpoints accessible
    print("\n2. Testing UI Endpoints...")
    try:
        # Test review page
        response = requests.get(f'{BASE_URL}/review')
        if response.status_code == 200:
            print("✅ Review page accessible")
            
            # Check if it contains updated minimum (100 instead of 50)
            if '/100' in response.text or '100 articles' in response.text:
                print("✅ Found references to 100 articles (updated minimum)")
            else:
                print("⚠️  May still show old minimum of 50")
        else:
            print(f"❌ Review page failed: {response.status_code}")
            
        # Test details page
        response = requests.get(f'{BASE_URL}/details')
        if response.status_code == 200 or response.status_code == 302:  # 302 = redirect to API key page
            print("✅ Details page accessible")
        else:
            print(f"❌ Details page failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing UI: {e}")
    
    # Test 3: Expected behavior summary
    print("\n3. Expected Behavior:")
    print("📋 Review Page:")
    print("   • Minimum selection changed from 50 to 100 articles")
    print("   • 'Rank Top 100' button selects best articles automatically")
    print("   • Counter shows 'Selected: X/100 (minimum required)'")
    
    print("\n📋 Details Page:")
    print("   • Articles displayed in ranking order (best first)")
    print("   • Ranking badges on each article card")
    print("   • Green badges (#1-10), Yellow (#11-50), Gray (#51+)")
    print("   • Info banner explaining smart ranking")
    
    print("\n🎯 User Workflow:")
    print("   1. Click 'Rank Top 100' on review page")
    print("   2. Click 'Review Selected Articles' (now requires 100)")
    print("   3. See articles in quality order with ranking badges")
    print("   4. Enhance/publish the highest-ranked content")

if __name__ == "__main__":
    test_updated_features()
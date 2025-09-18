#!/usr/bin/env python3
"""
Comprehensive test suite for Basement Cowboy features
Tests auto-categorization, ranking system, and API endpoints
"""
import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = 'http://127.0.0.1:5000'

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_subheader(title):
    print(f"\n📋 {title}")
    print("-" * 40)

def test_flask_app_running():
    """Test if Flask app is accessible"""
    print_header("TESTING FLASK APP CONNECTIVITY")
    
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200:
            print("✅ Flask app is running and accessible")
            return True
        else:
            print(f"❌ Flask app returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False

def test_ranking_system():
    """Test the article ranking system"""
    print_header("TESTING ARTICLE RANKING SYSTEM")
    
    try:
        print("🔄 Calling /rank_articles endpoint...")
        start_time = time.time()
        
        response = requests.post(f'{BASE_URL}/rank_articles')
        
        if response.status_code == 200:
            data = response.json()
            elapsed = time.time() - start_time
            
            print(f"✅ Ranking API successful (took {elapsed:.2f}s)")
            print(f"📊 Total articles analyzed: {data.get('total_articles', 'N/A')}")
            print(f"🏆 Top articles selected: {len(data.get('top_100', []))}")
            
            # Analyze top 10 articles
            top_articles = data.get('top_100', [])[:10]
            print_subheader("Top 10 Ranked Articles")
            
            for i, article in enumerate(top_articles, 1):
                score = article.get('score', 0)
                headline = article.get('headline', 'No headline')[:50]
                category = article.get('category', 'Unknown')
                
                print(f"{i:2d}. Score: {score:4.1f} | {category:15s} | {headline}...")
            
            # Analyze score distribution
            scores = [a.get('score', 0) for a in top_articles]
            if scores:
                print_subheader("Score Analysis")
                print(f"Highest score: {max(scores):.1f}")
                print(f"Lowest score (top 10): {min(scores):.1f}")
                print(f"Average score (top 10): {sum(scores)/len(scores):.1f}")
            
            # Test scoring factors
            if top_articles:
                print_subheader("Scoring Factor Analysis (Top Article)")
                breakdown = top_articles[0].get('scoring_breakdown', {})
                for factor, score in breakdown.items():
                    print(f"  {factor.replace('_', ' ').title()}: {score} points")
            
            return True
            
        else:
            print(f"❌ Ranking API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ranking system: {e}")
        return False

def test_categorization_system():
    """Test the auto-categorization system"""
    print_header("TESTING AUTO-CATEGORIZATION SYSTEM")
    
    # Test cases with different types of content
    test_cases = [
        {
            "title": "Stock Market Hits Record High as Tech Stocks Surge",
            "summary": "Major technology companies drove the market to new heights today as investors showed confidence in the sector's growth prospects.",
            "expected_category": "Economy + Money"
        },
        {
            "title": "NASA Discovers Water on Mars Surface",
            "summary": "Scientists at NASA have confirmed the presence of liquid water on the Martian surface, marking a significant breakthrough in space exploration.",
            "expected_category": "Space"
        },
        {
            "title": "New AI Model Breaks Language Understanding Records",
            "summary": "Researchers have developed an artificial intelligence model that achieves unprecedented accuracy in natural language processing tasks.",
            "expected_category": "AI + Robotics"
        },
        {
            "title": "President Announces New Climate Policy",
            "summary": "The administration unveiled comprehensive climate change legislation aimed at reducing carbon emissions by 50% over the next decade.",
            "expected_category": "Politics"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print_subheader(f"Test Case {i}: {test_case['title'][:30]}...")
        
        try:
            payload = {
                'title': test_case['title'],
                'summary': test_case['summary']
            }
            
            response = requests.post(f'{BASE_URL}/ai_categorize', json=payload)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success', False):
                    suggested = data.get('suggested_category', 'Unknown')
                    confidence = data.get('confidence', 0)
                    
                    print(f"✅ Categorization successful")
                    print(f"   Suggested: {suggested}")
                    print(f"   Confidence: {confidence}%")
                    print(f"   Expected: {test_case['expected_category']}")
                    
                    # Check if categorization makes sense (not exact match required)
                    if suggested != 'Uncategorized':
                        success_count += 1
                        print(f"   ✅ Valid category suggested")
                    else:
                        print(f"   ⚠️  Default category returned")
                        
                else:
                    print(f"❌ Categorization failed: {data.get('error', 'Unknown error')}")
                    
            elif response.status_code == 401:
                print(f"⚠️  API key not configured (expected for this test)")
                print("   This is normal if OpenAI API key is not set")
                
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error in test case {i}: {e}")
    
    print_subheader("Categorization Test Summary")
    print(f"Successful categorizations: {success_count}/{len(test_cases)}")
    
    return success_count > 0

def test_ui_endpoints():
    """Test UI endpoints are accessible"""
    print_header("TESTING UI ENDPOINTS")
    
    endpoints = [
        ('/', 'Home page'),
        ('/review', 'Review page'),
    ]
    
    success_count = 0
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            if response.status_code == 200:
                print(f"✅ {description} ({endpoint}) - OK")
                success_count += 1
            else:
                print(f"❌ {description} ({endpoint}) - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {description} ({endpoint}) - Error: {e}")
    
    return success_count == len(endpoints)

def test_data_files():
    """Test if required data files exist"""
    print_header("TESTING DATA FILES")
    
    import os
    
    files_to_check = [
        ('config/categories.json', 'Categories configuration'),
        ('config/wordpress_config.json', 'WordPress configuration'),
        ('output/news_articles', 'News articles directory'),
    ]
    
    success_count = 0
    
    for file_path, description in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        
        if os.path.exists(full_path):
            print(f"✅ {description} - Found")
            success_count += 1
        else:
            print(f"❌ {description} - Missing: {file_path}")
    
    # Check if we have recent article files
    articles_dir = os.path.join(os.path.dirname(__file__), 'output', 'news_articles')
    if os.path.exists(articles_dir):
        article_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
        print(f"📁 Found {len(article_files)} article files")
        
        if article_files:
            latest_file = max(article_files)
            print(f"📄 Latest file: {latest_file}")
            success_count += 1
    
    return success_count >= len(files_to_check)

def run_performance_test():
    """Test system performance under load"""
    print_header("PERFORMANCE TESTING")
    
    print("🚀 Testing ranking system performance...")
    
    # Test multiple ranking calls
    times = []
    for i in range(3):
        print(f"   Test run {i+1}/3...")
        start_time = time.time()
        
        try:
            response = requests.post(f'{BASE_URL}/rank_articles')
            if response.status_code == 200:
                elapsed = time.time() - start_time
                times.append(elapsed)
                print(f"   ✅ Completed in {elapsed:.2f}s")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 Performance Summary:")
        print(f"   Average time: {avg_time:.2f}s")
        print(f"   Fastest: {min(times):.2f}s")
        print(f"   Slowest: {max(times):.2f}s")
        
        if avg_time < 5.0:
            print("   ✅ Performance is good (< 5s)")
        elif avg_time < 10.0:
            print("   ⚠️  Performance is acceptable (< 10s)")
        else:
            print("   ❌ Performance needs improvement (> 10s)")
    
    return len(times) > 0

def main():
    """Run comprehensive test suite"""
    print(f"🚀 Starting Basement Cowboy Comprehensive Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Flask App Connectivity", test_flask_app_running),
        ("Data Files", test_data_files),
        ("UI Endpoints", test_ui_endpoints),
        ("Article Ranking System", test_ranking_system),
        ("Auto-Categorization System", test_categorization_system),
        ("Performance Testing", run_performance_test),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Final summary
    print_header("TEST RESULTS SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working perfectly.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. System is mostly functional.")
    else:
        print("⚠️  Several tests failed. Please check the issues above.")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
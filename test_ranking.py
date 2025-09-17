#!/usr/bin/env python3
"""
Quick test script to verify the ranking API is working
"""
import requests
import json

def test_ranking_api():
    try:
        print("🧪 Testing Ranking API...")
        
        # Test the ranking endpoint
        response = requests.post('http://127.0.0.1:5000/rank_articles')
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ SUCCESS! Ranking API is working")
            print(f"📊 Total articles analyzed: {data['total_articles']}")
            print(f"🏆 Top 100 selected: {len(data['top_100'])}")
            
            # Show top 5 ranked articles
            print(f"\n🥇 Top 5 Ranked Articles:")
            for i, article in enumerate(data['top_100'][:5]):
                print(f"{i+1}. Score: {article['score']} - {article['headline'][:60]}...")
            
            # Show scoring breakdown for top article
            if data['top_100']:
                top_article = data['top_100'][0]
                print(f"\n📈 Top Article Scoring Breakdown:")
                for factor, score in top_article.get('scoring_breakdown', {}).items():
                    print(f"  {factor}: {score} points")
            
            print(f"\n📋 Scoring System:")
            for factor, description in data.get('scoring_summary', {}).items():
                print(f"  {factor}: {description}")
                
        else:
            print(f"❌ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask app. Is it running on http://127.0.0.1:5000?")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_ranking_api()
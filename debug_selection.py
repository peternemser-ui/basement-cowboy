#!/usr/bin/env python3
"""
Debug script to test the article selection logic
"""
import json
import os

def test_selection_logic():
    # Simulate the URL parameters from your screenshot
    selected_indices_param = "0,1,293,19,19,547,40,669,2,96,12,3,12,96"
    
    print(f"Testing selected_indices_param: '{selected_indices_param}'")
    
    # Test the parsing logic
    if selected_indices_param:
        try:
            selected_indices = [int(idx.strip()) for idx in selected_indices_param.split(',') if idx.strip()]
            print(f"Parsed selected_indices: {selected_indices[:10]}... (showing first 10)")
            print(f"Total selected indices: {len(selected_indices)}")
            
            # Load articles from the latest file
            articles_dir = 'output/news_articles'
            files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
            files.sort()
            latest_file = files[-1]
            print(f"Loading from: {latest_file}")
            
            with open(os.path.join(articles_dir, latest_file), 'r', encoding='utf-8') as f:
                all_articles = json.load(f)
            
            print(f"Total articles in file: {len(all_articles)}")
            
            # Test article selection
            selected_articles = []
            for idx in selected_indices:
                if 0 <= idx < len(all_articles):
                    selected_articles.append(all_articles[idx])
                else:
                    print(f"WARNING: Index {idx} is out of range (max: {len(all_articles)-1})")
            
            print(f"Successfully selected {len(selected_articles)} articles")
            
            # Show first few articles
            for i, article in enumerate(selected_articles[:3]):
                print(f"Article {i}: {article.get('title', 'No title')[:50]}...")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No selected_indices_param provided")

if __name__ == "__main__":
    test_selection_logic()
#!/usr/bin/env python3
"""
Simple test to debug the article selection issue
"""
import os
import json

def test_url_params():
    # Simulate the URL parameters from your screenshots
    selected_indices_param = "0,1,293,19,19,547,40,669,2,96,12,3,12,96,32,9,96,670,1,54"
    file_param = "news_articles_2025-10-08-2.json"  # This should be the file from the review page
    
    print(f"Testing with:")
    print(f"  selected_indices: {selected_indices_param}")
    print(f"  file: {file_param}")
    print()
    
    # Test the file loading logic
    articles_dir = 'output/news_articles'
    all_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
    print(f"Available files: {all_files}")
    
    # Check if the requested file exists
    if file_param in all_files:
        target_file = os.path.join(articles_dir, file_param)
        print(f"Loading requested file: {file_param}")
    else:
        # Use latest file
        latest = sorted(all_files, reverse=True)[0]
        target_file = os.path.join(articles_dir, latest)
        print(f"Requested file not found, using latest: {latest}")
    
    # Load articles
    with open(target_file, 'r', encoding='utf-8') as f:
        all_articles = json.load(f)
    
    print(f"Total articles in file: {len(all_articles)}")
    
    # Test the selection logic
    selected_articles = []
    
    if selected_indices_param:
        try:
            selected_indices = [int(idx.strip()) for idx in selected_indices_param.split(',') if idx.strip()]
            print(f"Parsed {len(selected_indices)} indices: {selected_indices[:10]}...")
            
            for idx in selected_indices:
                if 0 <= idx < len(all_articles):
                    selected_articles.append(all_articles[idx])
                else:
                    print(f"WARNING: Index {idx} out of range (max: {len(all_articles)-1})")
            
            print(f"Successfully selected {len(selected_articles)} articles")
            
            # Test articles_by_category logic
            articles_by_category = {}
            for article in selected_articles:
                cat = article.get('category', 'Uncategorized')
                if cat not in articles_by_category:
                    articles_by_category[cat] = []
                articles_by_category[cat].append(article)
            
            print(f"Categories: {list(articles_by_category.keys())}")
            total_by_category = sum(len(arts) for arts in articles_by_category.values())
            print(f"Total articles by category: {total_by_category}")
            
            # This is what should be passed to template
            print(f"\nTemplate variables:")
            print(f"  articles length: {len(selected_articles)}")
            print(f"  selected_articles length: {len(selected_articles)}")
            print(f"  articles_by_category total: {total_by_category}")
            
        except Exception as e:
            print(f"Error in selection logic: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No selected_indices parameter")

if __name__ == "__main__":
    test_url_params()
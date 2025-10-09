#!/usr/bin/env python3
"""
Direct test script to debug article selection issue
"""
import os
import json

def test_article_selection():
    print("=== DIRECT ARTICLE SELECTION TEST ===")
    
    # Simulate the parameters from the review page
    selected_indices_param = "0,1,2,3,4,5,6,7,8,9"  # First 10 articles
    file_param = ""  # Empty, should use latest file
    
    print(f"Selected indices param: {selected_indices_param}")
    print(f"File param: '{file_param}'")
    
    try:
        # Parse indices (same logic as routes.py)
        selected_indices = [int(idx.strip()) for idx in selected_indices_param.split(',') if idx.strip()]
        print(f"Parsed indices: {selected_indices}")
        print(f"Total selected: {len(selected_indices)}")
        
        # Load articles (same logic as routes.py)
        base_dir = os.path.abspath(os.path.dirname(__file__))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        print(f"Looking for articles in: {articles_dir}")
        
        all_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
        print(f"Found {len(all_files)} JSON files")
        
        if file_param and file_param in all_files:
            target_file = os.path.join(articles_dir, file_param)
            print(f"Using specified file: {file_param}")
        else:
            if not all_files:
                print("ERROR: No JSON files found!")
                return
            latest_file = sorted(all_files, reverse=True)[0]
            target_file = os.path.join(articles_dir, latest_file)
            print(f"Using latest file: {latest_file}")
        
        print(f"Loading file: {target_file}")
        with open(target_file, 'r', encoding='utf-8') as f:
            all_articles = json.load(f)
        
        print(f"Total articles in file: {len(all_articles)}")
        
        # Select articles (same logic as routes.py)
        selected_articles = []
        for idx in selected_indices:
            if 0 <= idx < len(all_articles):
                selected_articles.append(all_articles[idx])
                title = all_articles[idx].get('headline', all_articles[idx].get('title', 'No title'))
                print(f"  Added article {idx}: {title[:50]}...")
            else:
                print(f"  WARNING: Index {idx} is out of range!")
        
        print(f"\nFINAL RESULT:")
        print(f"Selected {len(selected_articles)} articles")
        
        if selected_articles:
            print("\nFirst 3 selected articles:")
            for i, article in enumerate(selected_articles[:3]):
                title = article.get('headline', article.get('title', 'No title'))
                print(f"  {i}: {title[:50]}...")
        else:
            print("ERROR: No articles were selected!")
            
        return selected_articles
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_article_selection()
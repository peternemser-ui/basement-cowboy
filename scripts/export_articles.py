#!/usr/bin/env python3
"""Export articles to various formats."""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path


ARTICLES_DIR = Path('output/news_articles')


def load_articles(status_filter: str = None, category_filter: str = None) -> list:
    """Load articles from storage."""
    articles = []

    if not ARTICLES_DIR.exists():
        return articles

    for file_path in ARTICLES_DIR.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                article = json.load(f)

            # Apply filters
            if status_filter and article.get('status') != status_filter:
                continue
            if category_filter and article.get('category') != category_filter:
                continue

            articles.append(article)
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}", file=sys.stderr)

    # Sort by scraped_at (newest first)
    articles.sort(
        key=lambda a: a.get('scraped_at', ''),
        reverse=True
    )

    return articles


def export_json(articles: list, output_file: Path, pretty: bool = True):
    """Export articles to JSON format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        else:
            json.dump(articles, f, ensure_ascii=False)

    print(f"Exported {len(articles)} articles to {output_file}")


def export_jsonl(articles: list, output_file: Path):
    """Export articles to JSON Lines format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

    print(f"Exported {len(articles)} articles to {output_file}")


def export_csv(articles: list, output_file: Path):
    """Export articles to CSV format."""
    if not articles:
        print("No articles to export.")
        return

    # Define columns
    columns = [
        'id', 'title', 'url', 'source_name', 'category', 'author',
        'scraped_at', 'status', 'rank_score', 'image_url', 'excerpt'
    ]

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()

        for article in articles:
            # Flatten source
            row = {**article}
            if 'source' in row and isinstance(row['source'], dict):
                row['source_name'] = row['source'].get('name', '')
            writer.writerow(row)

    print(f"Exported {len(articles)} articles to {output_file}")


def export_markdown(articles: list, output_file: Path):
    """Export articles to Markdown format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Exported Articles\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total articles: {len(articles)}\n\n")
        f.write("---\n\n")

        for article in articles:
            f.write(f"## {article.get('title', 'Untitled')}\n\n")

            # Metadata
            source = article.get('source', {})
            source_name = source.get('name', 'Unknown') if isinstance(source, dict) else 'Unknown'
            f.write(f"- **Source:** {source_name}\n")
            f.write(f"- **URL:** {article.get('url', 'N/A')}\n")

            if article.get('author'):
                f.write(f"- **Author:** {article['author']}\n")
            if article.get('category'):
                f.write(f"- **Category:** {article['category']}\n")
            if article.get('scraped_at'):
                f.write(f"- **Scraped:** {article['scraped_at']}\n")
            if article.get('rank_score'):
                f.write(f"- **Rank Score:** {article['rank_score']:.2f}\n")

            f.write("\n")

            # Content
            if article.get('excerpt'):
                f.write(f">{article['excerpt']}\n\n")

            if article.get('content'):
                # Truncate long content
                content = article['content'][:1000]
                if len(article['content']) > 1000:
                    content += '...'
                f.write(f"{content}\n\n")

            f.write("---\n\n")

    print(f"Exported {len(articles)} articles to {output_file}")


def export_html(articles: list, output_file: Path):
    """Export articles to HTML format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exported Articles</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        .article { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .article h2 { margin-top: 0; }
        .article h2 a { color: #333; text-decoration: none; }
        .article h2 a:hover { color: #1976d2; }
        .meta { color: #666; font-size: 0.9em; margin-bottom: 10px; }
        .meta span { margin-right: 15px; }
        .excerpt { color: #444; font-style: italic; }
        .badge { background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>Exported Articles</h1>
    <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f"</p>\n")
        f.write(f"    <p>Total articles: {len(articles)}</p>\n")

        for article in articles:
            source = article.get('source', {})
            source_name = source.get('name', 'Unknown') if isinstance(source, dict) else 'Unknown'

            f.write('    <div class="article">\n')
            f.write(f'        <h2><a href="{article.get("url", "#")}" target="_blank">{article.get("title", "Untitled")}</a></h2>\n')
            f.write('        <div class="meta">\n')
            f.write(f'            <span class="badge">{article.get("category", "General")}</span>\n')
            f.write(f'            <span>{source_name}</span>\n')
            if article.get('author'):
                f.write(f'            <span>By {article["author"]}</span>\n')
            f.write('        </div>\n')
            if article.get('excerpt'):
                f.write(f'        <p class="excerpt">{article["excerpt"]}</p>\n')
            f.write('    </div>\n')

        f.write("""</body>
</html>""")

    print(f"Exported {len(articles)} articles to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Export articles to various formats'
    )
    parser.add_argument(
        'output',
        help='Output file path'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['json', 'jsonl', 'csv', 'markdown', 'html'],
        help='Output format (auto-detected from extension if not specified)'
    )
    parser.add_argument(
        '--status', '-s',
        choices=['scraped', 'ranked', 'enhanced', 'published'],
        help='Filter by status'
    )
    parser.add_argument(
        '--category', '-c',
        help='Filter by category'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of articles'
    )
    parser.add_argument(
        '--compact',
        action='store_true',
        help='Compact JSON output (no pretty printing)'
    )

    args = parser.parse_args()

    output_file = Path(args.output)

    # Auto-detect format from extension
    format_type = args.format
    if not format_type:
        ext = output_file.suffix.lower()
        format_map = {
            '.json': 'json',
            '.jsonl': 'jsonl',
            '.csv': 'csv',
            '.md': 'markdown',
            '.html': 'html',
        }
        format_type = format_map.get(ext, 'json')

    # Load articles
    articles = load_articles(
        status_filter=args.status,
        category_filter=args.category
    )

    if not articles:
        print("No articles found matching criteria.")
        return

    # Apply limit
    if args.limit:
        articles = articles[:args.limit]

    # Export
    if format_type == 'json':
        export_json(articles, output_file, pretty=not args.compact)
    elif format_type == 'jsonl':
        export_jsonl(articles, output_file)
    elif format_type == 'csv':
        export_csv(articles, output_file)
    elif format_type == 'markdown':
        export_markdown(articles, output_file)
    elif format_type == 'html':
        export_html(articles, output_file)


if __name__ == '__main__':
    main()

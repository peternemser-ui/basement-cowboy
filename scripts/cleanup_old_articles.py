#!/usr/bin/env python3
"""Script to clean up old articles and free up storage."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


ARTICLES_DIR = Path('output/news_articles')
CACHE_DIR = Path('output/cache')
LOGS_DIR = Path('output/logs')


def get_file_age_days(file_path: Path) -> float:
    """Get file age in days."""
    mtime = file_path.stat().st_mtime
    age = datetime.now().timestamp() - mtime
    return age / (24 * 60 * 60)


def get_article_age_days(file_path: Path) -> float:
    """Get article age based on scraped_at field."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scraped_at = data.get('scraped_at')
        if scraped_at:
            dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
            age = datetime.now().timestamp() - dt.timestamp()
            return age / (24 * 60 * 60)
    except Exception:
        pass
    # Fall back to file modification time
    return get_file_age_days(file_path)


def format_size(size_bytes: int) -> str:
    """Format file size for display."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def cleanup_articles(max_age_days: int, dry_run: bool = True) -> dict:
    """Clean up old articles."""
    stats = {'deleted': 0, 'kept': 0, 'bytes_freed': 0}

    if not ARTICLES_DIR.exists():
        return stats

    for file_path in ARTICLES_DIR.glob('*.json'):
        age = get_article_age_days(file_path)

        if age > max_age_days:
            size = file_path.stat().st_size
            if dry_run:
                print(f"  Would delete: {file_path.name} ({age:.1f} days old)")
            else:
                file_path.unlink()
                print(f"  Deleted: {file_path.name}")
            stats['deleted'] += 1
            stats['bytes_freed'] += size
        else:
            stats['kept'] += 1

    return stats


def cleanup_cache(max_age_days: int, dry_run: bool = True) -> dict:
    """Clean up old cache files."""
    stats = {'deleted': 0, 'bytes_freed': 0}

    if not CACHE_DIR.exists():
        return stats

    for file_path in CACHE_DIR.glob('*.json'):
        age = get_file_age_days(file_path)

        if age > max_age_days:
            size = file_path.stat().st_size
            if dry_run:
                print(f"  Would delete: {file_path.name}")
            else:
                file_path.unlink()
            stats['deleted'] += 1
            stats['bytes_freed'] += size

    return stats


def cleanup_logs(max_age_days: int, dry_run: bool = True) -> dict:
    """Clean up old log files."""
    stats = {'deleted': 0, 'bytes_freed': 0}

    if not LOGS_DIR.exists():
        return stats

    for file_path in LOGS_DIR.glob('*'):
        if file_path.is_file():
            age = get_file_age_days(file_path)

            if age > max_age_days:
                size = file_path.stat().st_size
                if dry_run:
                    print(f"  Would delete: {file_path.name}")
                else:
                    file_path.unlink()
                stats['deleted'] += 1
                stats['bytes_freed'] += size

    return stats


def get_storage_stats() -> dict:
    """Get current storage statistics."""
    stats = {
        'articles': {'count': 0, 'size': 0},
        'cache': {'count': 0, 'size': 0},
        'logs': {'count': 0, 'size': 0},
    }

    if ARTICLES_DIR.exists():
        for f in ARTICLES_DIR.glob('*.json'):
            stats['articles']['count'] += 1
            stats['articles']['size'] += f.stat().st_size

    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob('*'):
            if f.is_file():
                stats['cache']['count'] += 1
                stats['cache']['size'] += f.stat().st_size

    if LOGS_DIR.exists():
        for f in LOGS_DIR.glob('*'):
            if f.is_file():
                stats['logs']['count'] += 1
                stats['logs']['size'] += f.stat().st_size

    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Clean up old articles and cache files'
    )
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=7,
        help='Delete items older than this many days (default: 7)'
    )
    parser.add_argument(
        '--articles',
        action='store_true',
        help='Clean up old articles'
    )
    parser.add_argument(
        '--cache',
        action='store_true',
        help='Clean up cache files'
    )
    parser.add_argument(
        '--logs',
        action='store_true',
        help='Clean up log files'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Clean up all (articles, cache, logs)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show storage statistics'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompt'
    )

    args = parser.parse_args()

    # Show stats
    if args.stats:
        stats = get_storage_stats()
        print("\nStorage Statistics:")
        print("-" * 40)
        for category, data in stats.items():
            print(f"  {category.capitalize()}: {data['count']} files ({format_size(data['size'])})")
        total_size = sum(d['size'] for d in stats.values())
        print(f"  Total: {format_size(total_size)}")
        return

    # Determine what to clean
    clean_articles = args.articles or args.all
    clean_cache = args.cache or args.all
    clean_logs = args.logs or args.all

    if not any([clean_articles, clean_cache, clean_logs]):
        parser.print_help()
        print("\nSpecify what to clean: --articles, --cache, --logs, or --all")
        return

    # Confirmation
    if not args.dry_run and not args.force:
        print(f"\nThis will permanently delete files older than {args.days} days.")
        response = input("Continue? [y/N]: ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return

    dry_run = args.dry_run
    total_deleted = 0
    total_freed = 0

    if dry_run:
        print("\n[DRY RUN] - No files will actually be deleted\n")

    # Clean articles
    if clean_articles:
        print(f"Cleaning articles older than {args.days} days...")
        stats = cleanup_articles(args.days, dry_run)
        print(f"  Articles: {stats['deleted']} deleted, {stats['kept']} kept")
        total_deleted += stats['deleted']
        total_freed += stats['bytes_freed']

    # Clean cache
    if clean_cache:
        print(f"\nCleaning cache older than {args.days} days...")
        stats = cleanup_cache(args.days, dry_run)
        print(f"  Cache files: {stats['deleted']} deleted")
        total_deleted += stats['deleted']
        total_freed += stats['bytes_freed']

    # Clean logs
    if clean_logs:
        print(f"\nCleaning logs older than {args.days} days...")
        stats = cleanup_logs(args.days, dry_run)
        print(f"  Log files: {stats['deleted']} deleted")
        total_deleted += stats['deleted']
        total_freed += stats['bytes_freed']

    # Summary
    print("\n" + "=" * 40)
    action = "Would delete" if dry_run else "Deleted"
    print(f"{action} {total_deleted} files ({format_size(total_freed)})")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Health check script for Basement Cowboy."""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime


def check_mark(passed: bool) -> str:
    """Return check mark or x for status."""
    return "✅" if passed else "❌"


def check_directories() -> dict:
    """Check required directories exist."""
    directories = [
        'output/news_articles',
        'output/wordpress-output',
        'output/logs',
        'output/cache',
        'config',
        'data',
    ]

    results = {}
    for dir_path in directories:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        results[dir_path] = exists

    return results


def check_config_files() -> dict:
    """Check configuration files exist."""
    files = [
        'config/top_100_news_sites.txt',
        'config/categories.json',
    ]

    results = {}
    for file_path in files:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        results[file_path] = exists

    return results


def check_environment() -> dict:
    """Check environment variables."""
    variables = [
        ('OPENAI_API_KEY', True),  # (name, is_secret)
        ('WORDPRESS_URL', False),
        ('WORDPRESS_USERNAME', False),
        ('WORDPRESS_PASSWORD', True),
    ]

    results = {}
    for var_name, is_secret in variables:
        value = os.environ.get(var_name)
        if is_secret and value:
            results[var_name] = "****" + value[-4:] if len(value) > 4 else "****"
        else:
            results[var_name] = value if value else None

    return results


def check_dependencies() -> dict:
    """Check Python dependencies."""
    packages = [
        'flask',
        'requests',
        'beautifulsoup4',
        'openai',
        'playwright',
    ]

    results = {}
    for package in packages:
        try:
            __import__(package.replace('-', '_').replace('4', ''))
            results[package] = True
        except ImportError:
            results[package] = False

    return results


def check_disk_space() -> dict:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        return {
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'percent_used': round(used / total * 100, 1),
        }
    except Exception as e:
        return {'error': str(e)}


def check_article_storage() -> dict:
    """Check article storage status."""
    articles_dir = Path('output/news_articles')
    if not articles_dir.exists():
        return {'count': 0, 'size_mb': 0}

    files = list(articles_dir.glob('*.json'))
    total_size = sum(f.stat().st_size for f in files)

    return {
        'count': len(files),
        'size_mb': round(total_size / (1024**2), 2),
    }


def check_api_connectivity() -> dict:
    """Check API connectivity."""
    results = {}

    # Check local API
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        results['local_api'] = response.status_code == 200
    except Exception:
        results['local_api'] = False

    # Check OpenAI API (just connectivity, not auth)
    try:
        response = requests.get('https://api.openai.com', timeout=5)
        results['openai_reachable'] = response.status_code < 500
    except Exception:
        results['openai_reachable'] = False

    return results


def run_health_check(verbose: bool = True) -> dict:
    """Run complete health check."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # Directories
    if verbose:
        print("\n📁 Checking directories...")
    dir_results = check_directories()
    results['checks']['directories'] = dir_results
    if verbose:
        for path, exists in dir_results.items():
            print(f"  {check_mark(exists)} {path}")

    # Config files
    if verbose:
        print("\n📄 Checking config files...")
    config_results = check_config_files()
    results['checks']['config_files'] = config_results
    if verbose:
        for path, exists in config_results.items():
            print(f"  {check_mark(exists)} {path}")

    # Environment
    if verbose:
        print("\n🔐 Checking environment variables...")
    env_results = check_environment()
    results['checks']['environment'] = {k: bool(v) for k, v in env_results.items()}
    if verbose:
        for var, value in env_results.items():
            status = "Set" if value else "Not set"
            print(f"  {check_mark(bool(value))} {var}: {status}")

    # Dependencies
    if verbose:
        print("\n📦 Checking dependencies...")
    dep_results = check_dependencies()
    results['checks']['dependencies'] = dep_results
    if verbose:
        for package, installed in dep_results.items():
            print(f"  {check_mark(installed)} {package}")

    # Disk space
    if verbose:
        print("\n💾 Checking disk space...")
    disk_results = check_disk_space()
    results['checks']['disk_space'] = disk_results
    if verbose:
        if 'error' in disk_results:
            print(f"  ❌ Error: {disk_results['error']}")
        else:
            status = disk_results['percent_used'] < 90
            print(f"  {check_mark(status)} {disk_results['free_gb']} GB free ({disk_results['percent_used']}% used)")

    # Article storage
    if verbose:
        print("\n📰 Checking article storage...")
    storage_results = check_article_storage()
    results['checks']['article_storage'] = storage_results
    if verbose:
        print(f"  ✅ {storage_results['count']} articles ({storage_results['size_mb']} MB)")

    # API connectivity
    if verbose:
        print("\n🌐 Checking API connectivity...")
    api_results = check_api_connectivity()
    results['checks']['api_connectivity'] = api_results
    if verbose:
        for api, reachable in api_results.items():
            print(f"  {check_mark(reachable)} {api}")

    # Overall status
    all_passed = all([
        all(dir_results.values()),
        all(config_results.values()),
        all(dep_results.values()),
        'error' not in disk_results,
    ])
    results['healthy'] = all_passed

    if verbose:
        print("\n" + "=" * 40)
        if all_passed:
            print("✅ Overall status: HEALTHY")
        else:
            print("⚠️  Overall status: ISSUES DETECTED")
        print("=" * 40)

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Health check for Basement Cowboy')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')

    args = parser.parse_args()

    results = run_health_check(verbose=not args.json and not args.quiet)

    if args.json:
        print(json.dumps(results, indent=2))

    sys.exit(0 if results['healthy'] else 1)


if __name__ == '__main__':
    main()

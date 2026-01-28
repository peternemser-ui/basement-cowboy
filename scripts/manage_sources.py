#!/usr/bin/env python3
"""CLI tool for managing news sources."""

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse


SOURCES_FILE = Path('config/top_100_news_sites.txt')


def load_sources() -> list:
    """Load sources from file."""
    if not SOURCES_FILE.exists():
        return []

    with open(SOURCES_FILE, 'r') as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]


def save_sources(sources: list):
    """Save sources to file."""
    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(SOURCES_FILE, 'w') as f:
        f.write("# News Sources for Basement Cowboy\n")
        f.write("# One URL per line\n\n")
        for source in sorted(set(sources)):
            f.write(f"{source}\n")


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def cmd_list(args):
    """List all sources."""
    sources = load_sources()

    if not sources:
        print("No sources configured.")
        return

    print(f"Configured news sources ({len(sources)}):\n")
    for i, source in enumerate(sources, 1):
        print(f"  {i:3}. {source}")


def cmd_add(args):
    """Add a new source."""
    url = args.url

    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    if not validate_url(url):
        print(f"Error: Invalid URL format: {url}")
        sys.exit(1)

    sources = load_sources()

    if url in sources:
        print(f"Source already exists: {url}")
        return

    sources.append(url)
    save_sources(sources)
    print(f"Added: {url}")
    print(f"Total sources: {len(sources)}")


def cmd_remove(args):
    """Remove a source."""
    target = args.url
    sources = load_sources()

    # Find matching sources
    matches = [s for s in sources if target.lower() in s.lower()]

    if not matches:
        print(f"No sources matching: {target}")
        return

    if len(matches) > 1 and not args.force:
        print("Multiple matches found:")
        for m in matches:
            print(f"  - {m}")
        print("\nBe more specific or use --force to remove all matches.")
        return

    for match in matches:
        sources.remove(match)
        print(f"Removed: {match}")

    save_sources(sources)
    print(f"Total sources: {len(sources)}")


def cmd_search(args):
    """Search sources."""
    query = args.query.lower()
    sources = load_sources()

    matches = [s for s in sources if query in s.lower()]

    if not matches:
        print(f"No sources matching: {args.query}")
        return

    print(f"Found {len(matches)} matching sources:\n")
    for source in matches:
        print(f"  - {source}")


def cmd_stats(args):
    """Show source statistics."""
    sources = load_sources()

    if not sources:
        print("No sources configured.")
        return

    # Group by domain
    domains = {}
    for source in sources:
        domain = urlparse(source).netloc
        domains[domain] = domains.get(domain, 0) + 1

    print(f"Source Statistics:")
    print(f"  Total sources: {len(sources)}")
    print(f"  Unique domains: {len(domains)}")
    print()

    # Top domains
    print("Top domains:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {domain}: {count}")


def cmd_validate(args):
    """Validate all sources."""
    sources = load_sources()
    invalid = []

    print("Validating sources...\n")

    for source in sources:
        if not validate_url(source):
            invalid.append(source)
            print(f"  ❌ Invalid: {source}")
        elif args.verbose:
            print(f"  ✅ Valid: {source}")

    if invalid:
        print(f"\nFound {len(invalid)} invalid sources.")
        if args.fix:
            for inv in invalid:
                sources.remove(inv)
            save_sources(sources)
            print("Invalid sources removed.")
    else:
        print(f"\nAll {len(sources)} sources are valid.")


def cmd_import(args):
    """Import sources from file."""
    import_file = Path(args.file)

    if not import_file.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    with open(import_file, 'r') as f:
        new_sources = [
            line.strip() for line in f
            if line.strip() and not line.startswith('#')
        ]

    existing = load_sources()
    added = 0

    for source in new_sources:
        if not source.startswith(('http://', 'https://')):
            source = 'https://' + source

        if validate_url(source) and source not in existing:
            existing.append(source)
            added += 1

    save_sources(existing)
    print(f"Imported {added} new sources.")
    print(f"Total sources: {len(existing)}")


def cmd_export(args):
    """Export sources to file."""
    sources = load_sources()
    output_file = Path(args.file)

    with open(output_file, 'w') as f:
        for source in sorted(sources):
            f.write(f"{source}\n")

    print(f"Exported {len(sources)} sources to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Manage news sources for Basement Cowboy'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    list_parser = subparsers.add_parser('list', help='List all sources')
    list_parser.set_defaults(func=cmd_list)

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new source')
    add_parser.add_argument('url', help='URL of the news source')
    add_parser.set_defaults(func=cmd_add)

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a source')
    remove_parser.add_argument('url', help='URL or domain to remove')
    remove_parser.add_argument('--force', '-f', action='store_true',
                               help='Remove all matches')
    remove_parser.set_defaults(func=cmd_remove)

    # Search command
    search_parser = subparsers.add_parser('search', help='Search sources')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=cmd_search)

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate sources')
    validate_parser.add_argument('--verbose', '-v', action='store_true')
    validate_parser.add_argument('--fix', action='store_true',
                                 help='Remove invalid sources')
    validate_parser.set_defaults(func=cmd_validate)

    # Import command
    import_parser = subparsers.add_parser('import', help='Import sources from file')
    import_parser.add_argument('file', help='File to import from')
    import_parser.set_defaults(func=cmd_import)

    # Export command
    export_parser = subparsers.add_parser('export', help='Export sources to file')
    export_parser.add_argument('file', help='File to export to')
    export_parser.set_defaults(func=cmd_export)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()

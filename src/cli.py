
import sys
import argparse
from pathlib import Path

from indexer import CodeIndexer
from search import CodeSearch


def cmd_index(args):
    """Index a directory."""
    indexer = CodeIndexer()
    
    print(f"\n⚡ Lightning Search - Indexer")
    print("=" * 60)
    
    # Index the directory
    success = indexer.index_directory(args.directory, pattern=args.pattern)
    
    if success == 0:
        print("\n❌ No files indexed\n")
        return 1
    
    # Print stats
    indexer.print_stats()
    
    # Save the index
    output_file = args.output or "index.json"
    print(f"\n💾 Saving index to {output_file}...")
    indexer.save(output_file)
    
    print(f"\n✅ Done! Use: lightning search '{args.directory.split('/')[-1]}' --index {output_file}")
    print()
    
    return 0


def cmd_search(args):
    """Search an index."""
    searcher = CodeSearch()
    
    # Check if index exists
    if not Path(args.index).exists():
        print(f"\n❌ Index file not found: {args.index}")
        print(f"💡 Run: lightning index <directory> first\n")
        return 1
    
    # Load index
    print(f"\n⚡ Lightning Search")
    print("=" * 60)
    print(f"\n📂 Loading index from {args.index}...")
    searcher.load_index(args.index)
    
    stats = searcher.indexer.get_stats()
    print(f"✅ Loaded {stats['files_indexed']} files, "
          f"{stats['functions_found']:,} functions\n")
    
    # Perform search
    results, search_time = searcher.search(args.query, limit=args.limit)
    searcher.display_results(results, search_time, args.query)
    
    return 0


def cmd_interactive(args):
    """Interactive search mode."""
    searcher = CodeSearch()
    
    # Check if index exists
    if not Path(args.index).exists():
        print(f"\n❌ Index file not found: {args.index}")
        print(f"💡 Run: lightning index <directory> first\n")
        return 1
    
    # Load index
    print("\n⚡ Lightning Search - Interactive Mode")
    print("=" * 60)
    print(f"\n📂 Loading index from {args.index}...")
    searcher.load_index(args.index)
    
    stats = searcher.indexer.get_stats()
    print(f"✅ Loaded {stats['files_indexed']} files, "
          f"{stats['functions_found']:,} functions\n")
    print("=" * 60)
    print("💡 Enter search queries (or 'quit' to exit)")
    print("=" * 60)
    
    # Interactive loop
    while True:
        try:
            query = input("\n🔎 Search: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not query:
                continue
            
            results, search_time = searcher.search(query, limit=args.limit)
            searcher.display_results(results, search_time, query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    return 0


def cmd_stats(args):
    """Show index statistics."""
    if not Path(args.index).exists():
        print(f"\n❌ Index file not found: {args.index}\n")
        return 1
    
    indexer = CodeIndexer()
    
    print("\n⚡ Lightning Search - Index Stats")
    print("=" * 60)
    print(f"\n📂 Loading {args.index}...")
    indexer.load(args.index)
    
    indexer.print_stats()
    
    # Additional stats
    stats = indexer.get_stats()
    print(f"\n📊 Additional Info:")
    print(f"{'Index file:':<20} {args.index}")
    
    # File size
    size_bytes = Path(args.index).stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print(f"{'File size:':<20} {size_mb:.2f} MB")
    
    if stats['files_indexed'] > 0:
        avg_per_file = size_mb / stats['files_indexed']
        print(f"{'Avg per file:':<20} {avg_per_file * 1024:.2f} KB")
    
    print()
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="⚡ Lightning Search - Blazingly fast code search for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index your project
  python cli.py index ./myproject -o myproject.index
  
  # Quick search
  python cli.py search "render_template" -i myproject.index
  
  # Search with more results
  python cli.py search "database" -i myproject.index -l 50
  
  # Interactive mode (best for exploration)
  python cli.py interactive -i myproject.index
  
  # Check index stats
  python cli.py stats -i myproject.index

Pro tip: Use interactive mode for exploring large codebases!

Project: https://github.com/SubhrajeetBhattacharjee/lightning-search
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Index command
    parser_index = subparsers.add_parser('index', help='Index a directory')
    parser_index.add_argument('directory', help='Directory to index')
    parser_index.add_argument('-o', '--output', help='Output index file (default: index.json)')
    parser_index.add_argument('-p', '--pattern', default='**/*.py', help='File pattern (default: **/*.py)')
    parser_index.set_defaults(func=cmd_index)
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search the index')
    parser_search.add_argument('query', help='Search query')
    parser_search.add_argument('-i', '--index', default='index.json', help='Index file (default: index.json)')
    parser_search.add_argument('-l', '--limit', type=int, default=20, help='Max results (default: 20)')
    parser_search.set_defaults(func=cmd_search)
    
    # Interactive command
    parser_interactive = subparsers.add_parser('interactive', help='Interactive search mode')
    parser_interactive.add_argument('-i', '--index', default='index.json', help='Index file (default: index.json)')
    parser_interactive.add_argument('-l', '--limit', type=int, default=20, help='Max results (default: 20)')
    parser_interactive.set_defaults(func=cmd_interactive)
    
    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show index statistics')
    parser_stats.add_argument('-i', '--index', default='index.json', help='Index file (default: index.json)')
    parser_stats.set_defaults(func=cmd_stats)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Run the command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
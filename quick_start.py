"""
Quick start script for Lightning Search demo.

This indexes the examples directory and launches interactive search.
Perfect for trying out Lightning Search!
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    print("""
    ⚡ Lightning Search - Quick Start Demo
    ====================================
    
    This will:
    1. Index the examples directory
    2. Launch interactive search mode
    3. Let you try some queries
    
    Press Enter to continue (or Ctrl+C to cancel)...
    """)
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled. See you later!\n")
        return
    
    # Check if we're in the right directory
    if not Path("src/cli.py").exists():
        print("\n❌ Error: Run this from the project root directory\n")
        return
    
    # Import our modules directly
    try:
        from core.indexer import CodeIndexer
        from core.search import CodeSearch
    except ImportError as e:
        print(f"\n❌ Error importing modules: {e}")
        print("Make sure you're running this with the virtual environment activated!\n")
        return
    
    print("\n📁 Step 1: Indexing examples directory...\n")
    
    # Index examples
    indexer = CodeIndexer()
    indexer.index_directory("examples")
    
    print("\n💾 Saving index...")
    indexer.save("quickstart.index")
    
    # Print stats
    indexer.print_stats()
    
    print("\n🔍 Step 2: Launching interactive search...\n")
    print("Try these queries:")
    print("  - 'add'")
    print("  - 'calculator'")
    print("  - 'multiply'")
    print("  - Type 'quit' to exit\n")
    print("=" * 60)
    
    # Launch interactive search
    searcher = CodeSearch()
    searcher.load_index("quickstart.index")
    
    search_history = []
    
    print("💡 Commands: search query, 'history', 'stats', or 'quit'\n")
    
    while True:
        try:
            query = input("🔎 Search: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if query.lower() == 'history':
                if search_history:
                    print("\n📜 Recent searches:")
                    for i, (q, count) in enumerate(search_history[-10:], 1):
                        print(f"   {i}. '{q}' ({count} results)")
                    print()
                else:
                    print("\n📜 No search history yet\n")
                continue
            
            if query.lower() == 'stats':
                print()
                indexer.print_stats()
                continue
            
            if not query:
                continue
            
            results, search_time = searcher.search(query, limit=20)
            searcher.display_results(results, search_time, query)
            
            search_history.append((query, len(results)))
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    print("\n✅ Demo complete! To use on your own projects:")
    print("   cd src")
    print("   python cli.py index ../your-project -o project.index")
    print("   python cli.py interactive -i project.index\n")


if __name__ == "__main__":
    main()
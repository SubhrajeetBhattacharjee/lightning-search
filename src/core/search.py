
import time
from typing import List, Dict, Any
from src.core.indexer import CodeIndexer


class CodeSearch:
   
    
    def __init__(self):
        """Initialize the search engine."""
        self.indexer = CodeIndexer()
        self.loaded = False
    
    def load_index(self, filepath: str = "index.json"):
        """
        Load an index file.
        
        Args:
            filepath: Path to the index file
        """
        self.indexer.load(filepath)
        self.loaded = True
    
    def search(self, query: str, limit: int = 20) -> tuple[List[Dict[str, Any]], float]:
       
        if not self.loaded:
            raise RuntimeError("No index loaded. Call load_index() first.")
        
        start_time = time.time()
        
        # Tokenize the query
        query_tokens = self.indexer.tokenizer.tokenize(query)
        
        if not query_tokens:
            return [], 0.0
        
        # Find results for each token
        all_results = []
        for token in query_tokens:
            if token in self.indexer.index:
                all_results.extend(self.indexer.index[token])
        
        # Remove duplicates (same file + line)
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result['file_id'], result['line'])
            if key not in seen:
                seen.add(key)
                # Add file path to result
                result['file_path'] = self.indexer.files[result['file_id']]['path']
                unique_results.append(result)
        
        # Sort by type (functions first, then classes, then imports)
        type_priority = {'function': 0, 'class': 1, 'import': 2}
        unique_results.sort(key=lambda x: type_priority.get(x['type'], 3))
        
        # Limit results
        limited_results = unique_results[:limit]
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return limited_results, search_time_ms
    
    def display_results(self, results: List[Dict[str, Any]], search_time_ms: float, query: str):
        """
        Display search results in a nice format.
        
        Args:
            results: List of search results
            search_time_ms: Time taken to search
            query: The original query
        """
        if not results:
            print(f"\n❌ No results found for '{query}'\n")
            return
        
        print(f"\n🔍 Found {len(results)} results for '{query}' in {search_time_ms:.2f}ms\n")
        print("=" * 70)
        
        current_file = None
        for i, result in enumerate(results, 1):
            # Print file header if it's a new file
            if result['file_path'] != current_file:
                current_file = result['file_path']
                print(f"\n📄 {current_file}")
            
            # Print the result
            type_emoji = {
                'function': '⚡',
                'class': '📦',
                'import': '📥'
            }
            emoji = type_emoji.get(result['type'], '📌')
            
            print(f"  {emoji} Line {result['line']:4d}: {result['name']}")
        
        print("\n" + "=" * 70)
        print(f"💡 Showing top {len(results)} results")
        print()


def main():
    """Interactive search demo."""
    import sys
    
    # Load the Flask index
    searcher = CodeSearch()
    
    print("🔍 Lightning Search - Interactive Mode")
    print("=" * 50)
    
    # Check if index file exists
    import os
    if not os.path.exists("flask_index.json"):
        print("\n❌ flask_index.json not found!")
        print("💡 Run: python test_flask.py first\n")
        sys.exit(1)
    
    print("\n📂 Loading Flask index...")
    searcher.load_index("flask_index.json")
    
    stats = searcher.indexer.get_stats()
    print(f"✅ Loaded {stats['files_indexed']} files, "
          f"{stats['functions_found']:,} functions\n")
    
    print("=" * 50)
    print("💡 Enter search queries (or 'quit' to exit)")
    print("=" * 50)
    
    # Interactive search loop
    while True:
        try:
            query = input("\n🔎 Search: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not query:
                continue
            
            # Perform search
            results, search_time = searcher.search(query, limit=20)
            searcher.display_results(results, search_time, query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
"""
Benchmark Lightning Search on major open-source projects.

Tests scaling from small (18k LOC) to massive (1M+ LOC).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from indexer import CodeIndexer
from search import CodeSearch


def count_lines(directory: str):
    """Count total lines of Python code."""
    total = 0
    for filepath in Path(directory).glob("**/*.py"):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                total += len(f.readlines())
        except:
            pass
    return total


def benchmark_project(name: str, directory: str):
    """Benchmark a single project."""
    
    if not Path(directory).exists():
        print(f"⚠️  {name} not found at {directory}")
        print(f"   Run: git clone [repo_url] {directory}\n")
        return None
    
    print(f"\n{'=' * 70}")
    print(f"📊 BENCHMARKING: {name}")
    print(f"{'=' * 70}\n")
    
    # Count files and lines
    python_files = list(Path(directory).glob("**/*.py"))
    num_files = len(python_files)
    
    print(f"📁 Counting lines of code...")
    num_lines = count_lines(directory)
    
    print(f"\n   Files: {num_files:,}")
    print(f"   Lines: {num_lines:,}")
    print(f"   Size:  {num_lines/1000:.1f}k LOC\n")
    
    # Index the project
    indexer = CodeIndexer()
    
    print("⏱️  Indexing (this may take a while for large projects)...\n")
    
    start_time = time.perf_counter()
    indexer.index_directory(directory)
    index_time = time.perf_counter() - start_time
    
    # Save index
    index_file = f"{name.lower().replace(' ', '_')}_big.index"
    indexer.save(index_file)
    
    # Get stats
    stats = indexer.get_stats()
    index_size_mb = Path(index_file).stat().st_size / (1024 * 1024)
    
    # Calculate rates
    files_per_sec = num_files / index_time if index_time > 0 else 0
    lines_per_sec = num_lines / index_time if index_time > 0 else 0
    
    print(f"\n✅ RESULTS:\n")
    print(f"{'Metric':<35} {'Value':>20}")
    print(f"{'-' * 55}")
    print(f"{'Indexing time':<35} {index_time:>18.2f}s")
    print(f"{'Files/second':<35} {files_per_sec:>18.1f}")
    print(f"{'Lines/second':<35} {lines_per_sec:>18,.0f}")
    print(f"{'Functions found':<35} {stats['functions_found']:>20,}")
    print(f"{'Classes found':<35} {stats['classes_found']:>20,}")
    print(f"{'Index size':<35} {index_size_mb:>18.2f} MB")
    print(f"{'Compression ratio':<35} {num_lines/1000/index_size_mb:>18.1f}x")
    
    # Test search performance
    print(f"\n🔍 Testing search speed...")
    searcher = CodeSearch()
    searcher.load_index(index_file)
    
    # Test queries
    test_queries = ["render", "request", "response", "init"]
    total_time = 0
    
    for query in test_queries:
        start = time.perf_counter()
        results, _ = searcher.search(query, limit=100)
        elapsed = (time.perf_counter() - start) * 1000
        total_time += elapsed
    
    avg_search_ms = total_time / len(test_queries)
    
    print(f"   Average search time: {avg_search_ms:.3f}ms")
    
    return {
        'name': name,
        'files': num_files,
        'lines': num_lines,
        'index_time': index_time,
        'files_per_sec': files_per_sec,
        'lines_per_sec': lines_per_sec,
        'functions': stats['functions_found'],
        'classes': stats['classes_found'],
        'index_size_mb': index_size_mb,
        'compression': num_lines/1000/index_size_mb,
        'search_time_ms': avg_search_ms
    }


def main():
    """Run benchmarks on all available projects."""
    
    print("\n⚡ LIGHTNING SEARCH - BIG PROJECT BENCHMARKS")
    print("=" * 70)
    print("\nThis will test Lightning Search on major open-source projects")
    print("from small (~18k LOC) to massive (1M+ LOC).\n")
    
    # Define projects to test
    projects = [
        ("Flask", "../test_repos/flask"),
        ("Requests", "../test_repos/requests"),
        ("Django", "../test_repos/django"),
        ("pandas", "../test_repos/pandas"),
        # ("CPython", "../test_repos/cpython"),  # Uncomment if you cloned it
    ]
    
    results = []
    
    # Benchmark each project
    for name, directory in projects:
        result = benchmark_project(name, directory)
        if result:
            results.append(result)
    
    # Summary table
    if results:
        print(f"\n{'=' * 70}")
        print(f"📊 SUMMARY - SCALING TEST")
        print(f"{'=' * 70}\n")
        
        print(f"{'Project':<15} {'LOC':>12} {'Time':>10} {'Rate':>15} {'Search':>12}")
        print(f"{'-' * 70}")
        
        for r in results:
            loc_display = f"{r['lines']/1000:.0f}k" if r['lines'] < 1000000 else f"{r['lines']/1000000:.1f}M"
            rate_display = f"{r['lines_per_sec']/1000:.0f}k/s"
            
            print(f"{r['name']:<15} {loc_display:>12} {r['index_time']:>9.1f}s "
                  f"{rate_display:>15} {r['search_time_ms']:>11.3f}ms")
        
        print(f"\n{'=' * 70}")
        print(f"✅ Tested from {results[0]['lines']:,} to {results[-1]['lines']:,} lines")
        print(f"   That's a {results[-1]['lines']/results[0]['lines']:.0f}x scale increase!")
        print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
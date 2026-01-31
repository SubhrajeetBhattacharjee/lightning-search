"""
Professional benchmark suite for Lightning Search.

Tests indexing and search performance on real projects.
"""

import sys
import time
import os
import psutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.indexer import CodeIndexer
from core.search import CodeSearch


class Benchmark:
    """Benchmark runner with detailed metrics."""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def get_memory_mb(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)
    
    def benchmark_indexing(self, directory: str, name: str):
        """
        Benchmark indexing performance.
        
        Returns detailed metrics.
        """
        print(f"\n{'=' * 70}")
        print(f"📊 BENCHMARK: {name}")
        print(f"{'=' * 70}\n")
        
        # Initial memory
        mem_start = self.get_memory_mb()
        
        # Create indexer
        indexer = CodeIndexer()
        
        # Count files first
        python_files = list(Path(directory).glob("**/*.py"))
        total_files = len(python_files)
        
        # Count lines
        total_lines = 0
        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        print(f"📁 Project: {name}")
        print(f"   Files: {total_files:,}")
        print(f"   Lines: {total_lines:,}\n")
        
        # Benchmark indexing
        print("⏱️  Indexing...")
        start_time = time.perf_counter()
        
        indexer.index_directory(directory)
        
        index_time = time.perf_counter() - start_time
        
        # Memory after indexing
        mem_after = self.get_memory_mb()
        mem_used = mem_after - mem_start
        
        # Save index
        index_file = f"{name.lower().replace(' ', '_')}_bench.index"
        indexer.save(index_file)
        
        # Get index size
        index_size_mb = Path(index_file).stat().st_size / (1024 * 1024)
        
        # Get stats
        stats = indexer.get_stats()
        
        # Print results
        print(f"\n✅ INDEXING RESULTS:\n")
        print(f"{'Metric':<30} {'Value':>20}")
        print(f"{'-' * 50}")
        print(f"{'Total time':<30} {index_time:>18.3f}s")
        print(f"{'Files/second':<30} {total_files/index_time:>18.1f}")
        print(f"{'Lines/second':<30} {total_lines/index_time:>18,.0f}")
        print(f"{'Functions found':<30} {stats['functions_found']:>20,}")
        print(f"{'Classes found':<30} {stats['classes_found']:>20,}")
        print(f"{'Unique tokens':<30} {stats['unique_tokens']:>20,}")
        print(f"{'Memory used':<30} {mem_used:>18.1f} MB")
        print(f"{'Index size on disk':<30} {index_size_mb:>18.2f} MB")
        print(f"{'Compression ratio':<30} {total_lines/1000/index_size_mb:>18.1f}x")
        
        return {
            'name': name,
            'files': total_files,
            'lines': total_lines,
            'index_time': index_time,
            'functions': stats['functions_found'],
            'classes': stats['classes_found'],
            'tokens': stats['unique_tokens'],
            'memory_mb': mem_used,
            'index_size_mb': index_size_mb,
            'index_file': index_file
        }
    
    def benchmark_search(self, index_file: str, queries: list):
        """Benchmark search performance."""
        print(f"\n{'=' * 70}")
        print(f"🔍 SEARCH BENCHMARKS")
        print(f"{'=' * 70}\n")
        
        # Load index
        searcher = CodeSearch()
        
        print("📂 Loading index...")
        load_start = time.perf_counter()
        searcher.load_index(index_file)
        load_time = (time.perf_counter() - load_start) * 1000  # ms
        
        print(f"✅ Loaded in {load_time:.2f}ms\n")
        
        # Run queries
        print(f"{'Query':<30} {'Results':>10} {'Time (ms)':>15}")
        print(f"{'-' * 55}")
        
        total_time = 0
        total_results = 0
        
        for query in queries:
            # Run query 10 times and take average
            times = []
            for _ in range(10):
                start = time.perf_counter()
                results, _ = searcher.search(query, limit=100)
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            total_time += avg_time
            total_results += len(results)
            
            print(f"{query:<30} {len(results):>10} {avg_time:>14.3f}")
        
        avg_query_time = total_time / len(queries)
        
        print(f"{'-' * 55}")
        print(f"{'Average':<30} {total_results//len(queries):>10} {avg_query_time:>14.3f}")
        
        return {
            'load_time_ms': load_time,
            'avg_query_time_ms': avg_query_time
        }


def main():
    """Run comprehensive benchmarks."""
    print("\n⚡ LIGHTNING SEARCH - BENCHMARK SUITE")
    print("=" * 70)
    
    bench = Benchmark()
    results = []
    
    # Define test projects
    projects = []
    
    # Check what's available
    if Path("../test_repos/flask").exists():
        projects.append(("../test_repos/flask", "Flask"))
    
    if Path("../examples").exists():
        projects.append(("../examples", "Examples (Small)"))
    
    if not projects:
        print("\n❌ No test projects found!")
        print("💡 Run: cd test_repos && git clone https://github.com/pallets/flask.git\n")
        return
    
    # Benchmark each project
    for directory, name in projects:
        result = bench.benchmark_indexing(directory, name)
        results.append(result)
    
    # Benchmark search on largest index
    if results:
        largest = max(results, key=lambda x: x['files'])
        
        test_queries = [
            "render",
            "template",
            "request",
            "response",
            "flask",
            "app",
            "route",
            "render template"
        ]
        
        search_results = bench.benchmark_search(largest['index_file'], test_queries)
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"📊 SUMMARY")
    print(f"{'=' * 70}\n")
    
    print(f"{'Project':<20} {'Files':>8} {'Lines':>10} {'Index Time':>12} {'Rate':>12}")
    print(f"{'-' * 70}")
    
    for r in results:
        rate = f"{r['files']/r['index_time']:.1f} f/s"
        print(f"{r['name']:<20} {r['files']:>8,} {r['lines']:>10,} "
              f"{r['index_time']:>11.2f}s {rate:>12}")
    
    if results:
        print(f"\n💡 Search Performance:")
        print(f"   Index load time: {search_results['load_time_ms']:.2f}ms")
        print(f"   Avg query time:  {search_results['avg_query_time_ms']:.3f}ms")
    
    print()


if __name__ == "__main__":
    main()
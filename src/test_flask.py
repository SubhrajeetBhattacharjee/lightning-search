from core.indexer import CodeIndexer

def main():
    print("=" * 60)
    print("🧪 BENCHMARKING: Flask Framework")
    print("=" * 60)

    indexer = CodeIndexer()

    indexer.index_directory("../test_repos/flask")

    indexer.print_stats()

    print("\n💾 Saving index...")
    indexer.save("flask_index.json")

    print("\n" + "=" * 60)
    print("✅ BENCHMARK COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
"""
Code indexer using inverted index for fast searching.

An inverted index maps tokens to their locations in code.
Think of it like a book index: word → page numbers.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
import logging

from parser import CodeParser
from tokenizer import Tokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeIndexer:
    """Build and manage an inverted index of code."""
    
    def __init__(self):
        """Initialize the indexer."""
        self.parser = CodeParser()
        self.tokenizer = Tokenizer()
        
        # The inverted index: token → list of locations
        self.index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # File metadata: file_id → file info
        self.files: Dict[int, Dict[str, Any]] = {}
        self.next_file_id = 0
        
        # Stats
        self.stats = {
            'files_indexed': 0,
            'functions_found': 0,
            'classes_found': 0,
            'imports_found': 0,
            'total_tokens': 0,
            'index_time': 0.0
        }
    
    def index_file(self, filepath: str) -> bool:
        """
        Index a single Python file.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse the file
            result = self.parser.parse_file(filepath)
            
            if 'error' in result:
                logger.warning(f"Skipping {filepath}: {result['error']}")
                return False
            
            # Assign file ID
            file_id = self.next_file_id
            self.next_file_id += 1
            
            # Store file metadata
            self.files[file_id] = {
                'path': result['filepath'],
                'functions': len(result['functions']),
                'classes': len(result['classes']),
                'imports': len(result['imports'])
            }
            
            # Index functions
            for func in result['functions']:
                self._index_item(func, file_id, 'function')
                self.stats['functions_found'] += 1
            
            # Index classes
            for cls in result['classes']:
                self._index_item(cls, file_id, 'class')
                self.stats['classes_found'] += 1
            
            # Index imports
            for imp in result['imports']:
                self._index_item(imp, file_id, 'import')
                self.stats['imports_found'] += 1
            
            self.stats['files_indexed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error indexing {filepath}: {e}")
            return False
    
    def _index_item(self, item: Dict[str, Any], file_id: int, item_type: str):
        """
        Add an item (function/class/import) to the index.
        
        Args:
            item: The parsed item (function, class, or import)
            file_id: ID of the file containing this item
            item_type: Type of item ('function', 'class', 'import')
        """
        # Get the text to tokenize
        if item_type == 'import':
            text = item.get('statement', '')
        else:
            text = item.get('name', '')
        
        if not text:
            return
        
        # Tokenize it
        tokens = self.tokenizer.tokenize(text)
        
        # Add docstring tokens if available
        if 'docstring' in item and item['docstring']:
            doc_tokens = self.tokenizer.tokenize(item['docstring'])
            tokens.extend(doc_tokens[:10])  # Limit docstring tokens
        
        # Add to inverted index
        for token in set(tokens):  # Use set to avoid duplicates
            self.index[token].append({
                'file_id': file_id,
                'line': item.get('line', 0),
                'name': text,
                'type': item_type
            })
            self.stats['total_tokens'] += 1
    
    def index_directory(self, directory: str, pattern: str = "**/*.py") -> int:
        """
        Index all Python files in a directory.
        
        Args:
            directory: Path to directory
            pattern: Glob pattern for files (default: **/*.py)
            
        Returns:
            Number of files successfully indexed
        """
        start_time = time.time()
        
        directory_path = Path(directory)
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory}")
            return 0
        
        # Find all Python files
        python_files = list(directory_path.glob(pattern))
        
        if not python_files:
            logger.warning(f"No Python files found in {directory}")
            return 0
        
        logger.info(f"Found {len(python_files)} Python files")
        
        # Index each file
        successful = 0
        for filepath in python_files:
            if self.index_file(str(filepath)):
                successful += 1
        
        self.stats['index_time'] = time.time() - start_time
        
        logger.info(f"Indexed {successful}/{len(python_files)} files in "
                   f"{self.stats['index_time']:.2f}s")
        
        return successful
    
    def get_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        return {
            **self.stats,
            'unique_tokens': len(self.index),
            'files': len(self.files)
        }
    
    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()
        
        print("\n📊 Index Statistics\n")
        print(f"{'Files indexed:':<20} {stats['files_indexed']:,}")
        print(f"{'Functions found:':<20} {stats['functions_found']:,}")
        print(f"{'Classes found:':<20} {stats['classes_found']:,}")
        print(f"{'Unique tokens:':<20} {stats['unique_tokens']:,}")
        print(f"{'Indexing time:':<20} {stats['index_time']:.2f}s")
        
        if stats['index_time'] > 0:
            rate = stats['files_indexed'] / stats['index_time']
            print(f"{'Indexing rate:':<20} {rate:.1f} files/sec")
    
    def save(self, filepath: str = "index.json"):
        """
        Save the index to disk.
        
        Args:
            filepath: Where to save the index
        """
        data = {
            'index': dict(self.index),  # Convert defaultdict to dict
            'files': self.files,
            'stats': self.stats,
            'next_file_id': self.next_file_id
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        # Get file size
        size_bytes = Path(filepath).stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        logger.info(f"Index saved to {filepath} ({size_mb:.2f} MB)")
    
    def load(self, filepath: str = "index.json"):
        """
        Load an index from disk.
        
        Args:
            filepath: Path to the saved index
        """
        start_time = time.time()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Restore data
        self.index = defaultdict(list, data['index'])
        self.files = {int(k): v for k, v in data['files'].items()}
        self.stats = data['stats']
        self.next_file_id = data['next_file_id']
        
        load_time = time.time() - start_time
        logger.info(f"Index loaded in {load_time:.3f}s")


def main():
    """Test the indexer."""
    indexer = CodeIndexer()
    
    # Index the examples directory
    print("🔍 Indexing examples directory...\n")
    indexer.index_directory("../examples")
    
    # Print stats
    indexer.print_stats()
    
    # Save it
    print("\n💾 Saving index...")
    indexer.save("test_index.json")
    
    # Test loading
    print("\n📂 Testing load...")
    indexer2 = CodeIndexer()
    indexer2.load("test_index.json")
    indexer2.print_stats()


if __name__ == "__main__":
    main()
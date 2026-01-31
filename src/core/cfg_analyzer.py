"""
CFG Analyzer - Analyze control flow of Python functions.

Integrates CFG builder with the parser to analyze real functions.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

from src.core.parser import CodeParser
from src.core.cfg_builder import CFGBuilder, ControlFlowGraph
import tree_sitter_python


class CFGAnalyzer:
    """Analyze control flow of Python functions."""
    
    def __init__(self):
        self.parser = CodeParser()
        self.cfg_builder = CFGBuilder()
    
    def analyze_file(self, filepath: str) -> List[ControlFlowGraph]:
        """
        Analyze all functions in a file.
        
        Returns list of CFGs, one per function.
        """
        # Parse the file
        result = self.parser.parse_file(filepath)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return []
        
        # Read the code
        with open(filepath, 'rb') as f:
            code = f.read()
        
        # Parse with Tree-sitter to get AST
        from tree_sitter import Language, Parser as TSParser
        
        ts_parser = TSParser(Language(tree_sitter_python.language()))
        tree = ts_parser.parse(code)
        
        # Find all function definitions
        cfgs = []
        
        def find_functions(node):
            """Recursively find function definitions."""
            if node.type == 'function_definition':
                # Build CFG for this function
                try:
                    cfg = self.cfg_builder.build_from_ast(node, code)
                    cfgs.append(cfg)
                except Exception as e:
                    print(f"⚠️  Warning: Could not build CFG: {e}")
            
            # Recurse
            for child in node.children:
                find_functions(child)
        
        find_functions(tree.root_node)
        
        return cfgs
    
    def analyze_function(self, filepath: str, function_name: str) -> Optional[ControlFlowGraph]:
        """
        Analyze a specific function by name.
        
        Returns CFG for that function, or None if not found.
        """
        cfgs = self.analyze_file(filepath)
        
        for cfg in cfgs:
            if cfg.function_name == function_name:
                return cfg
        
        return None
    
    def print_summary(self, cfgs: List[ControlFlowGraph]):
        """Print summary of all CFGs."""
        if not cfgs:
            print("\n❌ No functions found\n")
            return
        
        print(f"\n📊 CFG Analysis Summary")
        print("=" * 70)
        print(f"Functions analyzed: {len(cfgs)}\n")
        
        print(f"{'Function':<30} {'Blocks':>8} {'Edges':>8} {'Paths':>8} {'Complexity':>10}")
        print("-" * 70)
        
        for cfg in cfgs:
            stats = cfg.get_stats()
            # Cyclomatic complexity = edges - blocks + 2
            complexity = stats['edges'] - stats['blocks'] + 2
            
            print(f"{cfg.function_name:<30} {stats['blocks']:>8} {stats['edges']:>8} "
                  f"{stats['paths']:>8} {complexity:>10}")
        
        print()


def main():
    """Test CFG analyzer on real files."""
    import sys
    
    if len(sys.argv) < 2:
        print("\n⚡ CFG Analyzer - Control Flow Analysis")
        print("=" * 60)
        print("\nUsage:")
        print("  python cfg_analyzer.py <filepath>")
        print("  python cfg_analyzer.py <filepath> <function_name>")
        print("\nExamples:")
        print("  python cfg_analyzer.py ../examples/sample.py")
        print("  python cfg_analyzer.py ../examples/sample.py add")
        print()
        return
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"\n❌ File not found: {filepath}\n")
        return
    
    analyzer = CFGAnalyzer()
    
    if len(sys.argv) >= 3:
        # Analyze specific function
        function_name = sys.argv[2]
        print(f"\n🔍 Analyzing function: {function_name}")
        print("=" * 60)
        
        cfg = analyzer.analyze_function(filepath, function_name)
        
        if cfg:
            cfg.print_graph()
            
            # Print paths
            paths = cfg.get_all_paths()
            if paths:
                print(f"Found {len(paths)} execution paths:")
                for i, path in enumerate(paths, 1):
                    path_str = ' → '.join(f'Block{b}' for b in path)
                    print(f"  Path {i}: {path_str}")
                print()
        else:
            print(f"\n❌ Function '{function_name}' not found in {filepath}\n")
    
    else:
        # Analyze all functions
        print(f"\n🔍 Analyzing: {filepath}")
        print("=" * 60)
        
        cfgs = analyzer.analyze_file(filepath)
        
        if cfgs:
            analyzer.print_summary(cfgs)
            
            # Show detailed CFG for first function
            if cfgs:
                print(f"\n📊 Detailed CFG for: {cfgs[0].function_name}")
                cfgs[0].print_graph()
        else:
            print("\n❌ No functions found in file\n")


if __name__ == "__main__":
    main()
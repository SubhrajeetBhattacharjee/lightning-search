from typing import List, Dict, Set , Optional , Tuple
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)


@dataclass
class Variable:
    name: str
    defined_at: List[Tuple[int, int]] = field(default_factory=list)
    used_at: List[Tuple[int, int]] = field(default_factory=list)

       
    def add_definition(self, block_id: int, stmt_index: int):
        """Record where this variable is defined."""
        self.defined_at.append((block_id, stmt_index))
    
    def add_use(self, block_id: int, stmt_index: int):
        """Record where this variable is used."""
        self.used_at.append((block_id, stmt_index))
    
    def __repr__(self):
        return f"Variable({self.name}, defs={len(self.defined_at)}, uses={len(self.used_at)})"
    


class VariableTracker:
    """
    Track variables through a function.
    
    Identifies where variables are:
    - Defined (assigned)
    - Used (read)
    - Modified
    """
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
    
    def extract_from_cfg(self, cfg):
        """
        Extract variables from a CFG.
        
        Args:
            cfg: ControlFlowGraph instance
        """
        from cfg_builder import ControlFlowGraph
        
        # Process each basic block
        for block_id, block in cfg.blocks.items():
            # Process each statement in the block
            for stmt_index, stmt in enumerate(block.statements):
                self._analyze_statement(stmt, block_id, stmt_index)
    
    def _analyze_statement(self, stmt: str, block_id: int, stmt_index: int):
        """
        Analyze a single statement to find variable defs and uses.
        
        This is simplified - real implementation would use AST.
        """
        # Skip comments and docstrings
        stmt = stmt.strip()
        if not stmt or stmt.startswith('#') or stmt.startswith('"""'):
            return
        
        # Look for assignments (definitions)
        if '=' in stmt and not any(op in stmt for op in ['==', '!=', '<=', '>=']):
            self._extract_assignment(stmt, block_id, stmt_index)
        
        # Look for variable uses
        self._extract_uses(stmt, block_id, stmt_index)
    
    def _extract_assignment(self, stmt: str, block_id: int, stmt_index: int):
        """Extract variable definitions from assignment statements."""
        # Simple pattern: var = ...
        if '=' in stmt:
            parts = stmt.split('=', 1)
            lhs = parts[0].strip()
            
            # Handle simple assignments (not tuples for now)
            if ' ' not in lhs and ',' not in lhs and '[' not in lhs:
                var_name = lhs
                
                # Skip if it's a method call (has .)
                if '.' not in var_name and var_name.isidentifier():
                    if var_name not in self.variables:
                        self.variables[var_name] = Variable(var_name)
                    
                    self.variables[var_name].add_definition(block_id, stmt_index)
    
    def _extract_uses(self, stmt: str, block_id: int, stmt_index: int):
        """
        Extract variable uses (simplified version).
        
        Real implementation would use AST to accurately identify uses.
        """
        import re
        
        # Find potential variable names (identifiers)
        # This is a simplified heuristic
        potential_vars = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b', stmt)
        
        # Filter out keywords and builtins
        python_keywords = {
            'if', 'else', 'elif', 'for', 'while', 'def', 'class', 'return',
            'import', 'from', 'as', 'with', 'try', 'except', 'finally',
            'raise', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in',
            'is', 'True', 'False', 'None', 'self'
        }
        
        for var_name in potential_vars:
            if var_name not in python_keywords:
                # Track this as a use
                if var_name not in self.variables:
                    self.variables[var_name] = Variable(var_name)
                
                self.variables[var_name].add_use(block_id, stmt_index)
    
    def get_variable(self, name: str) -> Optional[Variable]:
        """Get variable by name."""
        return self.variables.get(name)
    
    def get_all_variables(self) -> List[Variable]:
        """Get all tracked variables."""
        return list(self.variables.values())
    
    def get_undefined_uses(self) -> List[Variable]:
        """
        Find variables that are used but never defined.
        
        These might be:
        - Function parameters
        - Global variables
        - Imported names
        - Bugs!
        """
        undefined = []
        for var in self.variables.values():
            if len(var.used_at) > 0 and len(var.defined_at) == 0:
                undefined.append(var)
        return undefined
    
    def get_unused_variables(self) -> List[Variable]:
        """
        Find variables that are defined but never used.
        
        Potential dead code!
        """
        unused = []
        for var in self.variables.values():
            if len(var.defined_at) > 0 and len(var.used_at) == 0:
                unused.append(var)
        return unused
    
    def print_summary(self):
        """Print a summary of variable tracking."""
        print("\n📊 Variable Tracking Summary")
        print("=" * 70)
        
        all_vars = sorted(self.get_all_variables(), key=lambda v: v.name)
        
        if not all_vars:
            print("No variables found")
            return
        
        print(f"\nTotal variables: {len(all_vars)}\n")
        
        print(f"{'Variable':<20} {'Definitions':>12} {'Uses':>8}")
        print("-" * 70)
        
        for var in all_vars[:20]:  # Show first 20
            print(f"{var.name:<20} {len(var.defined_at):>12} {len(var.used_at):>8}")
        
        if len(all_vars) > 20:
            print(f"\n... and {len(all_vars) - 20} more variables")
        
        # Show undefined uses
        undefined = self.get_undefined_uses()
        if undefined:
            print(f"\n⚠️  Variables used but not defined: {len(undefined)}")
            for var in undefined[:5]:
                print(f"   - {var.name} (used {len(var.used_at)} times)")
        
        # Show unused variables
        unused = self.get_unused_variables()
        if unused:
            print(f"\n💡 Variables defined but not used: {len(unused)}")
            for var in unused[:5]:
                print(f"   - {var.name}")
        
        print()


class DataFlowAnalyzer:
    """
    Complete data flow analyzer.
    
    Combines CFG with variable tracking.
    """
    
    def __init__(self):
        self.tracker = VariableTracker()
    
    def analyze_function(self, cfg, function_node=None, code=None):
        """
        Analyze data flow in a function.
        
        Uses AST when available for better accuracy.
        
        Args:
            cfg: ControlFlowGraph instance
            function_node: Tree-sitter function node (optional, for AST-based analysis)
            code: Source code bytes (optional)
            
        Returns:
            VariableTracker with analysis results
        """
        self.tracker = VariableTracker()
        
        # If we have AST node, use the better AST-based extractor
        if function_node is not None and code is not None:
            from variable_extractor import ASTVariableExtractor
            
            # Extract with AST (more accurate!)
            ast_extractor = ASTVariableExtractor()
            var_infos = ast_extractor.extract_from_function(function_node, code)
            
            # Convert to Variable objects
            for var_info in var_infos:
                if var_info.name not in self.tracker.variables:
                    self.tracker.variables[var_info.name] = Variable(var_info.name)
                
                var = self.tracker.variables[var_info.name]
                
                if var_info.is_definition:
                    var.add_definition(0, var_info.line)
                else:
                    var.add_use(0, var_info.line)
        else:
            # Fall back to regex-based extraction (less accurate)
            self.tracker.extract_from_cfg(cfg)
        
        return self.tracker


def main():
    """Test variable tracking on real code."""
    from cfg_analyzer import CFGAnalyzer
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        print("""
⚡ Data Flow Analyzer

Usage:
    python dataflow.py <file> <function>        # Analyze one function
    python dataflow.py <file> --all             # Analyze all functions
    python dataflow.py --test-flask             # Test on Flask

Examples:
    python dataflow.py ../examples/sample.py process_data
    python dataflow.py ../examples/sample.py --all
    python dataflow.py --test-flask
        """)
        return
    
    # Special mode: test on Flask
    if len(sys.argv) == 2 and sys.argv[1] == '--test-flask':
        test_on_flask()
        return
    
    filepath = sys.argv[1]
    
    if not Path(filepath).exists():
        print(f"\n❌ File not found: {filepath}\n")
        return
    
    # Analyze all functions in file
    if len(sys.argv) == 3 and sys.argv[2] == '--all':
        analyze_all_functions(filepath)
        return
    
    # Analyze specific function
    if len(sys.argv) < 3:
        print("❌ Please specify function name or use --all")
        return
    
    function_name = sys.argv[2]
    
    print(f"\n⚡ Data Flow Analysis")
    print("=" * 70)
    print(f"File: {filepath}")
    print(f"Function: {function_name}\n")
    
    # Build CFG first
    cfg_analyzer = CFGAnalyzer()
    cfg = cfg_analyzer.analyze_function(filepath, function_name)
    
    if not cfg:
        print(f"❌ Function '{function_name}' not found\n")
        return
    
   # Get AST node for better accuracy
    from parser import CodeParser
    parser_for_ast = CodeParser()
    function_node, code = parser_for_ast.get_function_node(filepath, function_name)
    
    # Analyze data flow with AST
    df_analyzer = DataFlowAnalyzer()
    tracker = df_analyzer.analyze_function(cfg, function_node, code)
    
    # Print results
    tracker.print_summary()
    
    # Show detailed info for a few variables
    all_vars = tracker.get_all_variables()
    if all_vars:
        print("\n📋 Detailed Variable Info (first 5):")
        print("-" * 70)
        
        for var in sorted(all_vars, key=lambda v: len(v.used_at), reverse=True)[:5]:
            print(f"\n{var.name}:")
            if var.defined_at:
                print(f"  Defined at: blocks {[b for b, _ in var.defined_at]}")
            if var.used_at:
                print(f"  Used at: blocks {[b for b, _ in var.used_at]} ({len(var.used_at)} times)")
        
        print()


def analyze_all_functions(filepath: str):
    """Analyze all functions in a file."""
    from cfg_analyzer import CFGAnalyzer
    
    print(f"\n⚡ Data Flow Analysis - All Functions")
    print("=" * 70)
    print(f"File: {filepath}\n")
    
    cfg_analyzer = CFGAnalyzer()
    cfgs = cfg_analyzer.analyze_file(filepath)
    
    if not cfgs:
        print("❌ No functions found\n")
        return
    
    print(f"Analyzing {len(cfgs)} functions...\n")
    
    # Analyze each function
    results = []
    df_analyzer = DataFlowAnalyzer()
    
    for cfg in cfgs:
        # Get AST node for this function
        from parser import CodeParser
        parser_for_ast = CodeParser()
        function_node, code = parser_for_ast.get_function_node(filepath, cfg.function_name)
        
        # Analyze with AST
        tracker = df_analyzer.analyze_function(cfg, function_node, code)
        
        # Collect stats
        all_vars = tracker.get_all_variables()
        undefined = tracker.get_undefined_uses()
        unused = tracker.get_unused_variables()
        
        results.append({
            'function': cfg.function_name,
            'total_vars': len(all_vars),
            'undefined': len(undefined),
            'unused': len(unused),
            'complexity': cfg.get_stats()['edges'] - cfg.get_stats()['blocks'] + 2
        })
    
    # Print summary table
    print(f"{'Function':<30} {'Variables':>10} {'Undefined':>10} {'Unused':>8} {'Complexity':>10}")
    print("-" * 70)
    
    for r in sorted(results, key=lambda x: x['total_vars'], reverse=True)[:20]:
        print(f"{r['function']:<30} {r['total_vars']:>10} {r['undefined']:>10} "
              f"{r['unused']:>8} {r['complexity']:>10}")
    
    if len(results) > 20:
        print(f"\n... and {len(results) - 20} more functions")
    
    print()


def test_on_flask():
    """Test data flow analysis on Flask codebase."""
    from pathlib import Path
    
    flask_path = Path("../test_repos/flask/src/flask/app.py")
    
    if not flask_path.exists():
        print("\n❌ Flask not found at ../test_repos/flask/")
        print("💡 Clone it first: cd ../test_repos && git clone https://github.com/pallets/flask.git\n")
        return
    
    print(f"\n⚡ TESTING ON FLASK - Production Code")
    print("=" * 70)
    print(f"File: {flask_path}\n")
    
    # Test on specific complex functions
    test_functions = [
        'dispatch_request',  # Moderate complexity
        'url_for',           # Complex
        'make_response',     # Very complex
        'run'                # Most complex
    ]
    
    from cfg_analyzer import CFGAnalyzer
    
    for func_name in test_functions:
        print(f"\n{'─' * 70}")
        print(f"Testing: {func_name}")
        print('─' * 70)
        
        cfg_analyzer = CFGAnalyzer()
        cfg = cfg_analyzer.analyze_function(str(flask_path), func_name)
        
        if cfg:
            df_analyzer = DataFlowAnalyzer()
            from parser import CodeParser
            parser_for_ast = CodeParser()
            function_node, code = parser_for_ast.get_function_node(str(flask_path), func_name)
            tracker = df_analyzer.analyze_function(cfg, function_node, code)
            
            all_vars = tracker.get_all_variables()
            undefined = tracker.get_undefined_uses()
            unused = tracker.get_unused_variables()
            
            print(f"\n  Total variables: {len(all_vars)}")
            print(f"  Undefined (params/imports): {len(undefined)}")
            print(f"  Unused: {len(unused)}")
            
            # Show most-used variables
            if all_vars:
                most_used = sorted(all_vars, key=lambda v: len(v.used_at), reverse=True)[:3]
                print(f"\n  Most used variables:")
                for var in most_used:
                    print(f"    - {var.name}: used {len(var.used_at)} times")
    
    print(f"\n{'=' * 70}")
    print("✅ Flask testing complete!")
    print("=" * 70)
    print("\nNow try: python dataflow.py ../test_repos/flask/src/flask/app.py --all")
    print()


if __name__ == "__main__":
    main()
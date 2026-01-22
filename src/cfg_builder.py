"""
Control Flow Graph (CFG) builder for Python functions.

A CFG represents all possible execution paths through a function.
Each node is a "basic block" - code that always executes together.

CURRENT LIMITATIONS (to be addressed in Week 2):
- TODO: Handle break/continue in loops
- TODO: Handle try/except/finally
- TODO: Handle with statements  
- TODO: Handle raise statements
- TODO: Flatten elif chains for cleaner CFG
- TODO: Split blocks on function calls that may raise
- TODO: Handle match/case (Python 3.10+)
- TODO: Handle short-circuit boolean logic (and/or)

For production use, these would be essential.
This is v1.0 - foundation for data flow analysis.
"""

from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BasicBlock:
    """
    A basic block - sequence of statements that execute together.
    
    Has one entry point and one exit point.
    """
    id: int
    statements: List[str] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)  # Blocks that can follow this one
    predecessors: List[int] = field(default_factory=list)  # Blocks that can come before
    block_type: str = "normal"  # normal, if_true, if_false, loop, return, exit
    
    def add_statement(self, stmt: str):
        """Add a statement to this block."""
        self.statements.append(stmt)
    
    def add_successor(self, block_id: int):
        """Add a successor block."""
        if block_id not in self.successors:
            self.successors.append(block_id)
    
    def add_predecessor(self, block_id: int):
        """Add a predecessor block."""
        if block_id not in self.predecessors:
            self.predecessors.append(block_id)
    
    def __repr__(self):
        return f"Block{self.id}[{self.block_type}]: {len(self.statements)} stmts"


class ControlFlowGraph:
    """
    Control Flow Graph for a function.
    
    Represents all possible execution paths.
    """
    
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.blocks: Dict[int, BasicBlock] = {}
        self.entry_block: Optional[int] = None
        self.exit_blocks: List[int] = []
        self.next_block_id = 0
    
    def create_block(self, block_type: str = "normal") -> BasicBlock:
        """Create a new basic block."""
        block = BasicBlock(id=self.next_block_id, block_type=block_type)
        self.blocks[self.next_block_id] = block
        self.next_block_id += 1
        return block
    
    def add_edge(self, from_block: int, to_block: int):
        """Add an edge between two blocks."""
        if from_block in self.blocks and to_block in self.blocks:
            self.blocks[from_block].add_successor(to_block)
            self.blocks[to_block].add_predecessor(from_block)
    
    def get_all_paths(self) -> List[List[int]]:
        """
        Get all possible execution paths from entry to exits.
        
        **WARNING:** This is a simplified implementation for demonstration.
        
        Limitations:
        - Does not handle loops correctly (can have infinite paths)
        - May miss valid paths in complex control flow
        - For production use, should use fixed-point analysis
        
        This method is useful for:
        - Simple functions without loops
        - Debugging and visualization
        - Understanding basic control flow
        
        For real static analysis, use data flow analysis instead.
        
        Returns:
            List of paths, where each path is a list of block IDs.
        """
        if self.entry_block is None:
            return []
        
        all_paths = []
        
        def dfs(current: int, path: List[int], visited: Set[int]):
            """Depth-first search to find all paths."""
            path.append(current)
            
            # If this is an exit block, save the path
            if current in self.exit_blocks:
                all_paths.append(path.copy())
            else:
                # Continue to successors
                for successor in self.blocks[current].successors:
                    # Avoid infinite loops (but allow revisiting in different paths)
                    if successor not in visited:
                        new_visited = visited.copy()
                        new_visited.add(current)
                        dfs(successor, path.copy(), new_visited)
            
        dfs(self.entry_block, [], set())
        return all_paths
    
    def get_stats(self) -> Dict[str, Any]:
        """Get CFG statistics."""
        return {
            'function': self.function_name,
            'blocks': len(self.blocks),
            'edges': sum(len(b.successors) for b in self.blocks.values()),
            'paths': len(self.get_all_paths()),
            'exit_blocks': len(self.exit_blocks)
        }
    
    def print_graph(self):
        """Print a text representation of the CFG."""
        print(f"\n📊 CFG for function: {self.function_name}")
        print("=" * 60)
        
        for block_id, block in sorted(self.blocks.items()):
            print(f"\n{block}")
            
            if block.statements:
                print("  Statements:")
                for stmt in block.statements[:3]:  # Show first 3
                    print(f"    - {stmt}")
                if len(block.statements) > 3:
                    print(f"    ... ({len(block.statements) - 3} more)")
            
            if block.successors:
                print(f"  → Successors: {block.successors}")
            
            if block.predecessors:
                print(f"  ← Predecessors: {block.predecessors}")
        
        print("\n" + "=" * 60)
        
        # Print stats
        stats = self.get_stats()
        print(f"Blocks: {stats['blocks']}, Edges: {stats['edges']}, Paths: {stats['paths']}")
        print()


class CFGBuilder:
    """
    Builds Control Flow Graphs from Python AST nodes.
    
    Takes a function AST and creates a CFG showing all execution paths.
    """
    
    def __init__(self):
        self.current_cfg: Optional[ControlFlowGraph] = None
        self.current_block: Optional[BasicBlock] = None
    
    def build_from_ast(self, function_node, code: bytes) -> ControlFlowGraph:
        """
        Build CFG from a Tree-sitter function node.
        
        Args:
            function_node: Tree-sitter node of type 'function_definition'
            code: The source code bytes
            
        Returns:
            ControlFlowGraph for this function
        """
        # Get function name
        name_node = function_node.child_by_field_name('name')
        if not name_node:
            function_name = "unknown"
        else:
            function_name = code[name_node.start_byte:name_node.end_byte].decode('utf8')
        
        # Create new CFG
        cfg = ControlFlowGraph(function_name)
        self.current_cfg = cfg
        
        # Create entry block
        entry = cfg.create_block(block_type="entry")
        cfg.entry_block = entry.id
        self.current_block = entry
        
        # Get function body
        body = function_node.child_by_field_name('body')
        
        if body:
            # Process the body
            exit_block = self._process_node(body, code, entry.id)
            
            # Always create a single EXIT node
            exit_node = cfg.create_block(block_type="exit")
            cfg.exit_blocks = [exit_node.id]
            
            # Connect all return statements to EXIT
            for block_id, block in cfg.blocks.items():
                if block.block_type == "return":
                    cfg.add_edge(block_id, exit_node.id)
            
            # If body has a normal exit path (non-return), connect it too
            if exit_block is not None and cfg.blocks[exit_block].block_type != "return":
                cfg.add_edge(exit_block, exit_node.id)
        
        return cfg
    
    def _process_node(self, node, code: bytes, current_block_id: int) -> Optional[int]:
        """
        Process an AST node and build CFG.
        
        Returns the ID of the last block in this control flow.
        """
        cfg = self.current_cfg
        
        if node.type == 'block':
            # Process each statement in the block
            last_block = current_block_id
            
            for child in node.children:
                if child.type not in [':', '{', '}', 'INDENT', 'DEDENT']:
                    last_block = self._process_node(child, code, last_block)
                    if last_block is None:
                        break  # Hit a return
            
            return last_block
        
        elif node.type == 'if_statement':
            return self._process_if(node, code, current_block_id)
        
        elif node.type == 'while_statement':
            return self._process_while(node, code, current_block_id)
        
        elif node.type == 'for_statement':
            return self._process_for(node, code, current_block_id)
        
        elif node.type == 'return_statement':
            # Add return to current block
            stmt = code[node.start_byte:node.end_byte].decode('utf8').strip()
            cfg.blocks[current_block_id].add_statement(stmt)
            cfg.blocks[current_block_id].block_type = "return"
            return None  # No successor (function exits)
        
        else:
            # Regular statement
            stmt = code[node.start_byte:node.end_byte].decode('utf8').strip()
            if stmt and stmt not in [':', 'pass']:
                cfg.blocks[current_block_id].add_statement(stmt)
            return current_block_id
    
    def _process_if(self, node, code: bytes, current_block_id: int) -> int:
        """Process if statement."""
        cfg = self.current_cfg
        
        # Create true and false branches
        true_block = cfg.create_block(block_type="if_true")
        false_block = cfg.create_block(block_type="if_false")
        merge_block = cfg.create_block(block_type="normal")
        
        # Add condition to current block
        condition = node.child_by_field_name('condition')
        if condition:
            cond_text = code[condition.start_byte:condition.end_byte].decode('utf8')
            cfg.blocks[current_block_id].add_statement(f"if {cond_text}")
        
        # Connect current to branches
        cfg.add_edge(current_block_id, true_block.id)
        cfg.add_edge(current_block_id, false_block.id)
        
        # Process true branch (consequence)
        consequence = node.child_by_field_name('consequence')
        if consequence:
            last_true = self._process_node(consequence, code, true_block.id)
            if last_true is not None:
                cfg.add_edge(last_true, merge_block.id)
        
        # Process false branch (alternative) if it exists
        alternative = node.child_by_field_name('alternative')
        if alternative:
            # TODO: Flatten elif chains for cleaner CFG (Week 2)
            last_false = self._process_node(alternative, code, false_block.id)
            if last_false is not None:
                cfg.add_edge(last_false, merge_block.id)
        else:
            # No else clause, false branch goes directly to merge
            cfg.add_edge(false_block.id, merge_block.id)
        
        return merge_block.id
    
    def _process_while(self, node, code: bytes, current_block_id: int) -> int:
        """Process while loop."""
        cfg = self.current_cfg
        
        # Create loop blocks
        loop_header = cfg.create_block(block_type="loop_header")
        loop_body = cfg.create_block(block_type="loop_body")
        loop_exit = cfg.create_block(block_type="normal")
        
        # Connect entry to loop header
        cfg.add_edge(current_block_id, loop_header.id)
        
        # Add condition
        condition = node.child_by_field_name('condition')
        if condition:
            cond_text = code[condition.start_byte:condition.end_byte].decode('utf8')
            cfg.blocks[loop_header.id].add_statement(f"while {cond_text}")
        
        # Loop header branches to body or exit
        cfg.add_edge(loop_header.id, loop_body.id)  # True: enter loop
        cfg.add_edge(loop_header.id, loop_exit.id)  # False: exit loop
        
        # Process loop body
        body = node.child_by_field_name('body')
        if body:
            last_body = self._process_node(body, code, loop_body.id)
            if last_body is not None:
                # Back edge: body loops back to header
                cfg.add_edge(last_body, loop_header.id)
        
        # TODO: Handle break/continue statements (Week 2)
        
        return loop_exit.id
    
    def _process_for(self, node, code: bytes, current_block_id: int) -> int:
        """
        Process for loop.
        
        Structure: for <target> in <iterator>: <body>
        
        Creates:
        - Loop header (evaluates iterator)
        - Loop body
        - Loop exit
        """
        cfg = self.current_cfg
        
        # Create loop blocks
        loop_header = cfg.create_block(block_type="for_header")
        loop_body = cfg.create_block(block_type="loop_body")
        loop_exit = cfg.create_block(block_type="normal")
        
        # Connect entry to loop header
        cfg.add_edge(current_block_id, loop_header.id)
        
        # Add for statement info
        # Get target and iterator
        left = node.child_by_field_name('left')  # loop variable
        right = node.child_by_field_name('right')  # iterable
        
        if left and right:
            left_text = code[left.start_byte:left.end_byte].decode('utf8')
            right_text = code[right.start_byte:right.end_byte].decode('utf8')
            cfg.blocks[loop_header.id].add_statement(f"for {left_text} in {right_text}")
        else:
            cfg.blocks[loop_header.id].add_statement("for loop")
        
        # Loop header branches to body or exit
        cfg.add_edge(loop_header.id, loop_body.id)  # Enter loop
        cfg.add_edge(loop_header.id, loop_exit.id)  # Exit loop
        
        # Process loop body
        body = node.child_by_field_name('body')
        if body:
            last_body = self._process_node(body, code, loop_body.id)
            if last_body is not None:
                # Back edge: body loops back to header
                cfg.add_edge(last_body, loop_header.id)
        
        # TODO: Handle break/continue statements (Week 2)
        
        return loop_exit.id


def main():
    """Test the CFG builder."""
    from parser import CodeParser
    
    # Test code
    test_code = """
def check_user(username):
    if username == "admin":
        return "Admin access"
    elif username:
        return "User access"
    else:
        return "No access"
"""
    
    # Parse it
    parser = CodeParser()
    
    # Write to temp file
    with open('temp_cfg_test.py', 'w') as f:
        f.write(test_code)
    
    # Parse
    result = parser.parse_file('temp_cfg_test.py')
    
    print("🔨 Building CFG...\n")
    
    # For demo, we'll build a simple CFG manually
    # (In reality, you'd extract the AST node from parser)
    
    cfg = ControlFlowGraph("check_user")
    
    # Entry
    entry = cfg.create_block("entry")
    cfg.entry_block = entry.id
    
    # If admin check
    admin_check = cfg.create_block("if_true")
    admin_check.add_statement("if username == 'admin'")
    
    # Branches
    return_admin = cfg.create_block("return")
    return_admin.add_statement("return 'Admin access'")
    
    elif_check = cfg.create_block("if_true")
    elif_check.add_statement("elif username")
    
    return_user = cfg.create_block("return")
    return_user.add_statement("return 'User access'")
    
    return_none = cfg.create_block("return")
    return_none.add_statement("return 'No access'")
    
    # Exit node (single exit design)
    exit_node = cfg.create_block("exit")
    
    # Connect blocks
    cfg.add_edge(entry.id, admin_check.id)
    cfg.add_edge(admin_check.id, return_admin.id)
    cfg.add_edge(admin_check.id, elif_check.id)
    cfg.add_edge(elif_check.id, return_user.id)
    cfg.add_edge(elif_check.id, return_none.id)
    
    # All returns connect to exit
    cfg.add_edge(return_admin.id, exit_node.id)
    cfg.add_edge(return_user.id, exit_node.id)
    cfg.add_edge(return_none.id, exit_node.id)
    
    cfg.exit_blocks = [exit_node.id]
    
    # Print it
    cfg.print_graph()
    
    # Get all paths
    paths = cfg.get_all_paths()
    print(f"Found {len(paths)} execution paths:")
    for i, path in enumerate(paths, 1):
        print(f"  Path {i}: {' → '.join(f'Block{b}' for b in path)}")
    
    # Clean up
    import os
    os.remove('temp_cfg_test.py')


if __name__ == "__main__":
    main()
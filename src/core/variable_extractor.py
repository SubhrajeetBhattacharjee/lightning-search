"""
Variable Extractor - Extract variables from Python AST.

Uses Tree-sitter to accurately identify variable definitions and uses.
"""

from typing import List, Set, Dict, Tuple
from dataclasses import dataclass


@dataclass
class VariableInfo:
    """Information about a variable occurrence."""
    name: str
    line: int
    column: int
    is_definition: bool  # True if this is where var is defined
    context: str  # 'assignment', 'parameter', 'loop_var', 'use'


class ASTVariableExtractor:
    """Extract variables from Tree-sitter AST nodes."""
    
    def __init__(self):
        self.variables: List[VariableInfo] = []
    
    def extract_from_function(self, function_node, code: bytes) -> List[VariableInfo]:
        """
        Extract all variables from a function.
        
        Args:
            function_node: Tree-sitter function_definition node
            code: Source code bytes
            
        Returns:
            List of VariableInfo
        """
        self.variables = []
        
        # Get function parameters (these are definitions)
        params = function_node.child_by_field_name('parameters')
        if params:
            self._extract_parameters(params, code)
        
        # Get function body
        body = function_node.child_by_field_name('body')
        if body:
            self._extract_from_body(body, code)
        
        return self.variables
    
    def _extract_parameters(self, params_node, code: bytes):
        """Extract function parameters."""
        for child in params_node.children:
            if child.type == 'identifier':
                name = code[child.start_byte:child.end_byte].decode('utf8')
                if name != 'self':  # Skip 'self'
                    self.variables.append(VariableInfo(
                        name=name,
                        line=child.start_point[0] + 1,
                        column=child.start_point[1],
                        is_definition=True,
                        context='parameter'
                    ))
    
    def _extract_from_body(self, body_node, code: bytes):
        """Extract variables from function body."""
        self._walk_tree(body_node, code)
    
    def _walk_tree(self, node, code: bytes):
        """Recursively walk AST and extract variables."""
        
        # Assignment: x = ...
        if node.type == 'assignment':
            left = node.child_by_field_name('left')
            if left and left.type == 'identifier':
                name = code[left.start_byte:left.end_byte].decode('utf8')
                self.variables.append(VariableInfo(
                    name=name,
                    line=left.start_point[0] + 1,
                    column=left.start_point[1],
                    is_definition=True,
                    context='assignment'
                ))
        
        # For loop: for x in ...
        elif node.type == 'for_statement':
            left = node.child_by_field_name('left')
            if left and left.type == 'identifier':
                name = code[left.start_byte:left.end_byte].decode('utf8')
                self.variables.append(VariableInfo(
                    name=name,
                    line=left.start_point[0] + 1,
                    column=left.start_point[1],
                    is_definition=True,
                    context='loop_var'
                ))
        
        # Variable use: just an identifier
        elif node.type == 'identifier':
            # Check if this is a use (not a definition)
            parent = node.parent
            if parent and parent.type not in ['assignment', 'for_statement']:
                name = code[node.start_byte:node.end_byte].decode('utf8')
                if name not in ['self', 'True', 'False', 'None']:
                    self.variables.append(VariableInfo(
                        name=name,
                        line=node.start_point[0] + 1,
                        column=node.start_point[1],
                        is_definition=False,
                        context='use'
                    ))
        
        # Recurse to children
        for child in node.children:
            self._walk_tree(child, code)


def main():
    """Test variable extraction."""
    from core.parser import CodeParser
    
    # Test code
    test_code = """
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
    
    # Write to temp file
    with open('temp_var_test.py', 'w') as f:
        f.write(test_code)
    
    # Parse
    parser = CodeParser()
    node, code = parser.get_function_node('temp_var_test.py', 'process_data')
    
    if node:
        # Extract variables
        extractor = ASTVariableExtractor()
        variables = extractor.extract_from_function(node, code)
        
        print("\n📊 Variables Found:\n")
        
        # Group by type
        definitions = [v for v in variables if v.is_definition]
        uses = [v for v in variables if not v.is_definition]
        
        print(f"Definitions ({len(definitions)}):")
        for var in definitions:
            print(f"  {var.name} (line {var.line}) - {var.context}")
        
        print(f"\nUses ({len(uses)}):")
        for var in uses:
            print(f"  {var.name} (line {var.line})")
        
        print()
    
    # Cleanup
    import os
    os.remove('temp_var_test.py')


if __name__ == "__main__":
    main()
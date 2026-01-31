"""
Code parser using Tree-sitter.

This module handles parsing Python files and extracting searchable tokens.
Tree-sitter gives us a proper AST, which is way better than regex hacks.
"""

from tree_sitter import Language, Parser
import tree_sitter_python
from pathlib import Path
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeParser:
    """Parse Python files and extract semantic information."""
    
    def __init__(self):
        """Initialize the parser with Python language support."""
        # New API for tree-sitter >= 0.21
        parser = Parser(Language(tree_sitter_python.language()))
        self.parser = parser
        logger.info("Parser initialized with Python support")
    
    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """
        Parse a Python file and extract all searchable elements.
        
        Args:
            filepath: Path to the Python file
            
        Returns:
            Dictionary containing functions, classes, and other elements
            
        Example:
            >>> parser = CodeParser()
            >>> result = parser.parse_file("example.py")
            >>> print(result['functions'])
            [{'name': 'hello', 'line': 5, 'docstring': '...'}]
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return {'error': 'File not found'}
        
        try:
            with open(filepath, 'rb') as f:
                code = f.read()
            
            # Parse the code into an AST
            tree = self.parser.parse(code)
            root = tree.root_node
            
            # Extract different code elements
            result = {
                'filepath': str(filepath),
                'functions': [],
                'classes': [],
                'imports': [],
                'variables': [],
            }
            
            self._extract_elements(root, code, result)
            
            logger.debug(f"Parsed {filepath}: {len(result['functions'])} functions, "
                        f"{len(result['classes'])} classes")
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return {'error': str(e)}
    
    def _extract_elements(self, node, code: bytes, result: Dict):
        """
        Recursively extract code elements from AST.
        
        This is where we do the heavy lifting - walking the tree and
        finding all the interesting bits.
        """
        
        if node.type == 'function_definition':
            func_info = self._extract_function(node, code)
            if func_info:
                result['functions'].append(func_info)
        
        elif node.type == 'class_definition':
            class_info = self._extract_class(node, code)
            if class_info:
                result['classes'].append(class_info)
        
        elif node.type == 'import_statement' or node.type == 'import_from_statement':
            import_info = self._extract_import(node, code)
            if import_info:
                result['imports'].append(import_info)
        
        # Recurse through children
        for child in node.children:
            self._extract_elements(child, code, result)
    
    def _extract_function(self, node, code: bytes) -> Dict[str, Any]:
        """Extract function information."""
        name_node = node.child_by_field_name('name')
        
        if not name_node:
            return None
        
        name = code[name_node.start_byte:name_node.end_byte].decode('utf8')
        line = node.start_point[0] + 1
        
        # Try to get docstring
        docstring = None
        body = node.child_by_field_name('body')
        if body and len(body.children) > 0:
            first_statement = body.children[0]
            if first_statement.type == 'expression_statement':
                string_node = first_statement.children[0]
                if string_node.type == 'string':
                    docstring = code[string_node.start_byte:string_node.end_byte].decode('utf8')
                    # Clean up the docstring (remove quotes)
                    docstring = docstring.strip('"""').strip("'''").strip()
        
        return {
            'name': name,
            'line': line,
            'docstring': docstring,
            'type': 'function'
        }
    
    def _extract_class(self, node, code: bytes) -> Dict[str, Any]:
        """Extract class information."""
        name_node = node.child_by_field_name('name')
        
        if not name_node:
            return None
        
        name = code[name_node.start_byte:name_node.end_byte].decode('utf8')
        line = node.start_point[0] + 1
        
        return {
            'name': name,
            'line': line,
            'type': 'class'
        }
    
    def _extract_import(self, node, code: bytes) -> Dict[str, Any]:
        """Extract import information."""
        import_text = code[node.start_byte:node.end_byte].decode('utf8')
        line = node.start_point[0] + 1
        
        return {
            'statement': import_text,
            'line': line,
            'type': 'import'
        }

    def get_function_node(self, filepath: str, function_name: str):
        """
        Get the Tree-sitter AST node for a specific function.
        
        Args:
            filepath: Path to Python file
            function_name: Name of function to find
            
        Returns:
            Tuple of (function_node, code_bytes) or (None, None)
        """
        from pathlib import Path
        
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return None, None
        
        try:
            with open(filepath, 'rb') as f:
                code = f.read()
            
            tree = self.parser.parse(code)
            root = tree.root_node
            
            # Find the function
            def find_function(node):
                if node.type == 'function_definition':
                    name_node = node.child_by_field_name('name')
                    if name_node:
                        name = code[name_node.start_byte:name_node.end_byte].decode('utf8')
                        if name == function_name:
                            return node
                
                for child in node.children:
                    result = find_function(child)
                    if result:
                        return result
                
                return None
            
            function_node = find_function(root)
            
            if function_node:
                return function_node, code
            else:
                logger.warning(f"Function '{function_name}' not found in {filepath}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error getting function node: {e}")
            return None, None

def main():
    """Test the parser on itself (meta!)."""
    parser = CodeParser()
    
    # Parse this very file
    result = parser.parse_file(__file__)
    
    print(f"\n📄 Parsing: {result['filepath']}\n")
    
    print(f"✨ Functions found: {len(result['functions'])}")
    for func in result['functions']:
        print(f"  - {func['name']}() at line {func['line']}")
        if func['docstring']:
            # Show first line of docstring
            first_line = func['docstring'].split('\n')[0]
            print(f"    → {first_line}")
    
    print(f"\n📦 Classes found: {len(result['classes'])}")
    for cls in result['classes']:
        print(f"  - {cls['name']} at line {cls['line']}")
    
    print(f"\n📥 Imports found: {len(result['imports'])}")
    for imp in result['imports'][:5]:  # Show first 5
        print(f"  - {imp['statement']}")


if __name__ == "__main__":
    main()
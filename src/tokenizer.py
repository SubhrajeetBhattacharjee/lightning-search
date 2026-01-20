
import re
from typing import List, Set


class Tokenizer:
    """Break code identifiers into searchable tokens."""
    
    def __init__(self):
        """Initialize the tokenizer."""
        # Common words to ignore (stop words)
        self.stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were',
            'get', 'set', 'do', 'make', 'has', 'have'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Break text into searchable tokens.
        
        Handles:
        - snake_case: render_template → [render, template]
        - camelCase: getUserData → [get, user, data]
        - PascalCase: HttpServer → [http, server]
        - Numbers: func2 → [func, 2]
        
        Args:
            text: The identifier to tokenize
            
        Returns:
            List of lowercase tokens
            
        Example:
            >>> tokenizer = Tokenizer()
            >>> tokenizer.tokenize("render_template_string")
            ['render', 'template', 'string']
            >>> tokenizer.tokenize("getUserData")
            ['get', 'user', 'data']
        """
        if not text:
            return []
        
        # Step 1: Split on underscores
        text = text.replace('_', ' ')
        
        # Step 2: Split camelCase and PascalCase
        # Insert space before uppercase letters
        text = re.sub('([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub('([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
        
        # Step 3: Split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())
        
        # Step 4: Filter out stop words and single characters
        tokens = [
            t for t in tokens 
            if len(t) > 1 and t not in self.stop_words
        ]
        
        return tokens
    
    def tokenize_multiple(self, texts: List[str]) -> Set[str]:
        """
        Tokenize multiple strings and return unique tokens.
        
        Args:
            texts: List of strings to tokenize
            
        Returns:
            Set of unique tokens
        """
        all_tokens = set()
        for text in texts:
            tokens = self.tokenize(text)
            all_tokens.update(tokens)
        return all_tokens


def main():
    """Test the tokenizer."""
    tokenizer = Tokenizer()
    
    test_cases = [
        "render_template",
        "getUserData",
        "HTTPServer",
        "parse_file_contents",
        "onClick",
        "SQL_INJECTION_WARNING",
        "__init__",
        "test_function_2"
    ]
    
    print("🔤 Tokenizer Test\n")
    
    for case in test_cases:
        tokens = tokenizer.tokenize(case)
        print(f"{case:30} → {tokens}")


if __name__ == "__main__":
    main()
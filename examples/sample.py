
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.result = 0
    
    def add(self, a, b):
        """Add two numbers together."""
        return a + b
    
    def multiply(self, x, y):
        """Multiply two numbers."""
        return x * y


def greet(name):
    """Say hello to someone."""
    return f"Hello, {name}!"


def process_data(data):
    """
    Process some data.
    
    This function does important data processing.
    It's very sophisticated.
    """
    result = []
    for item in data:
        result.append(item * 2)
    return result


# Some random code
import os
import sys
from pathlib import Path

x = 42
y = "hello"
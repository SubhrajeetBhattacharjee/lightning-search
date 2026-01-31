"""
Utility functions for Lightning Search.
"""

def format_file_size(bytes_size: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def print_summary_box(title: str, items: dict):
    """Print a nice summary box."""
    print(f"\n╔{'═' * 58}╗")
    print(f"║ {title:^56} ║")
    print(f"╠{'═' * 58}╣")
    
    for key, value in items.items():
        print(f"║ {key:<30} {str(value):>25} ║")
    
    print(f"╚{'═' * 58}╝\n")
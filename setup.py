from setuptools import setup, find_packages

setup(
    name="lightning-search",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Blazingly fast code search for Python projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lightning-search",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "tree-sitter>=0.21.3",
        "tree-sitter-python>=0.21.0",
        "rich>=13.7.0",
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "msgpack>=1.0.7",
    ],
    entry_points={
        "console_scripts": [
            "lightning=src.cli:main",
        ],
    },
)
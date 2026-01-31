
# Lightning Search

Lightning Search is a fast code search and static analysis tool for Python codebases.

I built this while working with large Python repositories where traditional tools like `grep`, IDE search, or GitHub search were either slow or didn’t help me understand how the code actually behaves. Instead of repeatedly scanning files, Lightning Search indexes a codebase once and allows instant, structured exploration of the code.

The focus is on **understanding code**, not just matching text.

---

## What Lightning Search Does

Lightning Search provides two core capabilities.

### 1. Semantic Code Search

- Parses Python source code using an AST (Tree-sitter)
- Indexes functions, classes, imports, and identifiers
- Uses an inverted index for fast lookups
- Search results are typically returned in milliseconds after indexing

### 2. Control Flow Graph (CFG) Analysis

- Builds control flow graphs for real Python functions
- Computes cyclomatic complexity
- Enumerates execution paths
- Works on production code, not just small examples

---

## Typical Use Cases

- Exploring large or unfamiliar Python codebases
- Quickly locating important abstractions or APIs
- Identifying high-complexity functions
- Understanding how configuration or environment flags affect execution flow
- Reasoning about control flow without reading entire files manually

---

## Installation

```bash
git clone https://github.com/SubhrajeetBhattacharjee/lightning-search.git
cd lightning-search
pip install -r requirements.txt
````

---

## Indexing a Codebase

Indexing is a one-time operation.

```bash
python -m src.interfaces.cli index path/to/project -o project.index
```

Once indexed, all searches operate on the index without scanning files again.

---

## Searching

```bash
python -m src.interfaces.cli search "render_template" -i project.index
```

Search is symbol-based and AST-aware. It is not raw full-text search.

---

## Control Flow Analysis

Analyze all functions in a file:

```bash
python -m src.interfaces.cli cfg path/to/file.py
```

Analyze a specific function:

```bash
python -m src.interfaces.cli cfg path/to/file.py -f function_name
```

The output includes:

* Number of basic blocks
* Number of edges
* Cyclomatic complexity
* Execution path count
* Per-block structure for deeper inspection

---

## Benchmarks

Lightning Search has been tested on real-world Python codebases.

### Flask

* ~83 files
* Indexed in ~0.2 seconds
* Sub-millisecond search times
* Correct CFG metrics on production functions

### pandas

* ~1,500 files
* ~30,000 functions
* Index load time: ~0.26 seconds
* Typical search latency: ~5 milliseconds

Example:

```bash
python -m src.interfaces.cli search "DataFrame" -i benchmarks/pandas_big.index
```

This returns results instantly across the entire pandas codebase.

---

## Design Decisions

Some design choices are intentional.

**This is not full-text search**
Search focuses on meaningful program elements (symbols), not every keyword.

**Control flow is analyzed separately**
Keywords like `try` or `except` are handled via CFG analysis rather than search.

**No automatic re-indexing**
Indexing is explicit to keep behavior predictable and reproducible.

---

## Limitations

* Python-only support
* Intra-function CFG analysis (no cross-file analysis yet)
* No live file watching
* CLI-only interface

These are conscious trade-offs, not accidental omissions.

---

## Project Structure

```
src/
├── core/          # Parsing, indexing, CFG, and analysis logic
├── interfaces/    # CLI interface
```

The core logic is reusable and interface-agnostic.

---

## Why This Exists

This project was built to make understanding large Python codebases faster and more systematic. The goal is not to replace IDEs or linters, but to provide a lightweight tool for fast exploration and static analysis backed by real program structure.

---

## License

MIT License.

<img width="1382" height="376" alt="image" src="https://github.com/user-attachments/assets/0aaa67ec-001e-44d5-b51a-10ee4e71a66d" />

----------------------------------------------------------------------------------------------------------------------------------------


<img width="1002" height="832" alt="image" src="https://github.com/user-attachments/assets/dbc2be78-779a-4995-9de9-fa3a379f246a" />

----------------------------------------------------------------------------------------------------------------------------------------


<img width="937" height="947" alt="image" src="https://github.com/user-attachments/assets/7235694f-63e3-478d-83af-e10df6434e96" />


----------------------------------------------------------------------------------------------------------------------------------------



<img width="1130" height="976" alt="image" src="https://github.com/user-attachments/assets/f5489dc6-204a-4b6b-9894-5e833669b0b6" />





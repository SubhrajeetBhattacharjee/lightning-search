
# ⚡ Lightning Search

**Stop waiting. Start finding.**

Lightning Search is a **blazingly fast code search + static analysis tool for Python**.  
It indexes a codebase once and gives you **instant search**, plus **Control Flow Graph (CFG)** and **cyclomatic complexity** analysis.

> Think: **grep speed + code intelligence.**

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

---

## Why Lightning Search?

Ever done this?

```bash
$ grep -r "render_template" my-project/
# ... waits ...
# ... results finally appear ...
# ... but it doesn't understand code structure ...
````

Or GitHub search rate-limits you. Or your IDE struggles on large repos.

Lightning Search exists because **searching code should feel instant**.

---

## What It Does

Lightning Search indexes your Python codebase once, then lets you:

* ⚡ **Search instantly** (sub-millisecond query times)
* 🎯 **Find definitions** (functions, classes, imports)
* 🧠 **Understand structure** using AST parsing (Tree-sitter)
* 📊 **Analyze control flow** using CFG generation
* 🧮 **Compute cyclomatic complexity** for real functions

---

## Quick Start

### 1) Clone and install

```bash
git clone https://github.com/SubhrajeetBhattacharjee/lightning-search.git
cd lightning-search
pip install -r requirements.txt
```

### 2) Index a project

```bash
cd src
python cli.py index ../your-project -o project.index
```

### 3) Search

```bash
python cli.py search "render_template" -i project.index
```

### 4) Interactive mode (recommended)

```bash
python cli.py interactive -i project.index
```

### 5) View index stats

```bash
python cli.py stats -i project.index
```

---

## Real-World Performance (Benchmarked)

Benchmarked on: **Windows 11 • Python 3.12 • Intel i5 13th Gen • 32GB RAM**
All values are averages across multiple runs.

| Project |  LOC | Index Time | Avg Search Time |
| ------: | ---: | ---------: | --------------: |
|   Flask |  18k |      0.17s |          0.04ms |
|  Django | 508k |      5.15s |          0.25ms |
|  pandas | 651k |      6.26s |          0.13ms |

**651,000 lines indexed in ~6 seconds** and queries in **microseconds**.

> Note: These timings reflect **index-based lookup**, not raw file scanning.

---

## Examples

### 🔍 Basic Search

```bash
$ python cli.py search "render_template" -i flask.index

🔍 Found 18 results in 0.04ms

📄 flask/templating.py
  ⚡ Line  135: render_template
  ⚡ Line  150: render_template_string

📄 flask/helpers.py
  ⚡ Line  123: _render
```

### 📊 CFG + Complexity (Control Flow Analysis)

```bash
$ python cfg_analyze.py ../test_repos/flask/src/flask/app.py

📊 CFG Analysis Summary
Functions analyzed: 40

Function                         Blocks    Edges    Paths Complexity
----------------------------------------------------------------------
run                                  29       37       74         10
make_response                        26       33      108          9
url_for                              20       25       28          7
dispatch_request                      8        9        4          3
```

---

## Features

### 🚀 Fast Indexing

* Indexes large codebases at **~100k LOC/sec**
* Tested on Flask / Django / pandas
* Stores results as a persistent on-disk index

### ⚡ Instant Search

* **Sub-millisecond queries**
* Searches are performed in-memory using an inverted index
* Results include file path + line + symbol type

### 🧠 AST-Based Understanding

* Uses **Tree-sitter** to parse Python into an AST
* Extracts:

  * functions
  * classes
  * imports
  * docstrings (limited tokens)

### 📊 Control Flow Graphs (CFG)

* Builds CFGs using basic blocks + edges
* Supports:

  * if / elif / else
  * return exits
  * loop handling (in progress)
* Computes **cyclomatic complexity** using:

  * `V(G) = E - N + 2`

---

## How It Works (Architecture)

```text
Python Files
   ↓
Tree-sitter Parser (AST)
   ↓
Tokenizer (snake_case + camelCase)
   ↓
Inverted Index (token → locations)
   ↓
Search / CFG Analysis
   ↓
Saved Index (.index / JSON)
```

### Why It’s Fast

* Uses an **inverted index** (token → list of matches)
* Search is mostly **hash table lookup**
* No file I/O during search (after index is loaded)

---

## Commands

### Index a directory

```bash
python cli.py index <directory> -o <output.index>
```

### Search once

```bash
python cli.py search "<query>" -i <index-file> -l 20
```

### Interactive search

```bash
python cli.py interactive -i <index-file>
```

### Show stats

```bash
python cli.py stats -i <index-file>
```

---

## Limitations (Current)

Lightning Search is fast and stable, but still evolving.

**Currently supports:**

* ✅ Python-only indexing
* ✅ Function/class/import search
* ✅ CFG generation + complexity metrics

**Not yet supported:**

* ❌ Full-text search across every line (currently symbol/token focused)
* ❌ Real-time file watching (re-index required)
* ❌ Cross-file CFG/dataflow (coming soon)
* ❌ AI / natural language querying (planned)

---

## Roadmap

**✅ Phase 1: Foundation (DONE)**

* Tree-sitter parsing
* Tokenizer + inverted index
* CLI search + benchmarks
* CFG analysis + complexity reporting

**⏳ Phase 2: Data Flow Analysis**

* variable tracking (def-use)
* propagation across statements
* cross-function tracking (basic)

**⏳ Phase 3: Security Analysis**

* taint analysis (source → sink)
* SQL injection detection
* XSS detection
* path traversal detection

**⏳ Phase 4: AI Layer**

* natural language queries (local LLM via Ollama)
* vulnerability explanations
* fix suggestions

**⏳ Phase 5: Polish**

* VS Code extension
* real-time file watching
* multi-language support (JS / Go / Rust)
* PyPI package release (`pip install lightning-search`)

---

## Why I Built This

I was searching through a large codebase repeatedly.

* grep was slow and dumb
* GitHub search rate-limited
* IDE search lagged on big repos

So I built something that is:

✅ fast enough for real-time exploration
✅ structured enough to understand code
✅ extensible enough for static analysis

---

## Tech Stack

**Core**

* Python 3.9+
* Tree-sitter + tree-sitter-python
* Custom inverted index

**CLI**

* argparse
* tqdm

**Dev Tools**

* pytest (planned)
* black (optional)
* psutil (benchmarks)

---

## License

MIT License — see `LICENSE`.

---

## Contact

**Subhrajeet Bhattacharjee**

* GitHub: `@SubhrajeetBhattacharjee`
* Project: Lightning Search

---

⭐ If you find this useful, star the repo!

```

---




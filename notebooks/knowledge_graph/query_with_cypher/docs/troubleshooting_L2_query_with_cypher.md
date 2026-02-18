# Troubleshooting Guide: L2-query_with_cypher.ipynb

## Summary

This notebook connects to a Neo4j graph database (e.g. Neo4j AuraDB) and runs Cypher queries
against a standard movie/actor knowledge graph. Three issues were encountered and resolved
during initial setup:

1. **Missing Neo4j credentials** in `.env`
2. **Movie dataset not loaded** — Aura's Query console does not support `:play` or APOC, so the
   dataset must be loaded via the `load_movies.py` script
3. **`langchain_community` deprecated** — `Neo4jGraph` moved to the `langchain-neo4j` package

---

## Prerequisites

- Conda environment `agentic-ai` with `langchain-neo4j`, `neo4j`, and `python-dotenv` installed.
- A running Neo4j AuraDB instance (free tier is sufficient).
- Neo4j credentials in the **project-level `.env`** at `agentic-ai-lab/.env`:

  ```bash
  NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
  NEO4J_USERNAME=neo4j
  NEO4J_PASSWORD=<generated-password>
  NEO4J_DATABASE=neo4j
  ```

  The notebook uses `load_dotenv(find_dotenv(), override=True)`, which walks up the directory
  tree to find `.env` automatically — no need to place a separate `.env` in the notebook folder.

- Movie dataset loaded into the instance (see Error 2 below).

---

## Error 1: Missing Neo4j Credentials

### Symptom

```
RuntimeError: Missing Neo4j env: set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
```

Or a connection error when creating `Neo4jGraph`.

### Root Cause

The project-level `.env` does not have the four `NEO4J_*` variables set, or they still contain
the placeholder values from `.env.example`.

### Solution

1. Sign in to [Neo4j Aura](https://neo4j.com/cloud/aura/) and create an AuraDB instance
   (free tier works fine).
2. When the instance is created, Aura shows a one-time credentials dialog. Download the
   credentials file (contains URI and auto-generated password). If you missed it, reset the
   password: open the Aura Query console → run `ALTER USER neo4j SET PASSWORD 'NewPassword123'`.
3. Fill in `agentic-ai-lab/.env` with the four `NEO4J_*` values.
4. Restart the Jupyter kernel and re-run from the first cell.

---

## Error 2: Empty Database (queries return 0 nodes)

### Symptom

```python
[{'count(n)': 0}]
```

Queries run without error but return empty results.

### Root Cause

The AuraDB instance is blank. The movie dataset must be loaded manually.

**Why `:play movies` does not work**: The Aura Query console is a newer client that does not
support the classic `:play` guide commands (only available in Neo4j Browser / Desktop).

**Why APOC does not work**: AuraDB free/trial instances do not include the APOC plugin.

```
42N08: Syntax error or access rule violation – no such procedure
The procedure apoc.cypher.runScheme() was not found.
```

### Solution: run `load_movies.py`

A Python loader script is provided that connects via the `neo4j` driver and runs all `MERGE`
statements directly. It is idempotent (safe to re-run).

```bash
cd /Users/pleiadian53/work/agentic-ai-lab
conda activate agentic-ai
python notebooks/knowledge_graph/query_with_cypher/load_movies.py
```

Expected output:

```
Loading Neo4j movie dataset...
  Ran 301 statements.
  All statements succeeded.

Verifying...
  Node counts:
    Person               99
    Movie                35
  Relationships: 166

Done.
```

The script is at `notebooks/knowledge_graph/query_with_cypher/load_movies.py`.

---

## Error 3: `ModuleNotFoundError: No module named 'langchain_community'`

### Symptom

```
ModuleNotFoundError: No module named 'langchain_community'
```

Or (after installing `langchain-community`):

```
LangChainDeprecationWarning: The class `Neo4jGraph` was deprecated in LangChain 0.3.8
and will be removed in 1.0. An updated version of the class exists in the
`langchain-neo4j` package...
```

### Root Cause

`langchain-community` was not in `environment.yml`. When added, the import still produces a
deprecation warning because `Neo4jGraph` has been moved out of `langchain-community` into the
dedicated `langchain-neo4j` package.

### Solution

Install the updated package:

```bash
conda activate agentic-ai
pip install -U langchain-neo4j
```

Update imports (already fixed in the notebook):

**Before (deprecated):**
```python
from langchain_community.graphs import Neo4jGraph
```

**After (correct):**
```python
from langchain_neo4j import Neo4jGraph
```

Both `langchain-neo4j` and `langchain-community` are now in `environment.yml`.

---

## End-to-End Test

Run after credentials and dataset are in place:

```bash
cd /Users/pleiadian53/work/agentic-ai-lab
conda activate agentic-ai
python notebooks/knowledge_graph/query_with_cypher/test_L2_query_with_cypher_e2e.py
```

Expected: `ALL STEPS PASSED ✓`

The test uses `MERGE` for the "Andreas" person node so it is safe to run multiple times.

---

**Document created**: 2026-02-17  
**Last tested**: 2026-02-17  
**Tested with**: `langchain-neo4j==0.8.0`, `neo4j==6.1.0`, conda env `agentic-ai`, AuraDB Professional trial

# Knowledge Graph

Sub-project for exploring knowledge graph construction, querying, and integration with agentic AI systems within the `agentic-ai-lab` project.

## Overview

Knowledge graphs represent information as a network of entities and relationships. This sub-project covers:

- **Cypher Querying** — Pattern matching, CRUD operations, conditional filtering
- **KG Construction** — Building graphs from unstructured text using LLMs
- **Vector Embeddings on Graphs** — Adding text embeddings to node properties for vector similarity search
- **Graph-RAG** — Using knowledge graphs as the retrieval backend in RAG pipelines
- **Agentic KG Workflows** — Agents that read from and write to a knowledge graph

## Directory Structure

```
knowledge_graph/
├── __init__.py
├── README.md
├── utils/                 # Shared helpers (Neo4j connection, Cypher utilities, etc.)
│   └── __init__.py
├── docs/                  # KG-specific design notes and tutorials
└── examples/              # Custom KG apps and experiments
```

## Configuration

All Neo4j credentials are stored in the **project-level `.env`** (at the repo root):

```bash
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-neo4j-password
NEO4J_DATABASE=neo4j
```

Copy `.env.example` → `.env` at the repo root and fill in your credentials.

Code in this sub-project (and in `notebooks/knowledge_graph/`) uses `load_dotenv(find_dotenv())` to locate the root `.env` automatically, regardless of the working directory.

## Integration Path

Mature components will graduate to `src/agentic_core/` or `src/nexus/` as knowledge graph backing for agents:

- `src/nexus/knowledge/` — Nexus agent knowledge integration point
- `src/agentic_core/` — Core graph client and schema management

## Related

- `notebooks/knowledge_graph/` — Lesson notebooks and scratch space for KG experiments
- `rag/` — RAG sub-project (KG-backed retrieval is a natural integration point)
- `src/nexus/` — Nexus Research Agent (eventual consumer of KG components)

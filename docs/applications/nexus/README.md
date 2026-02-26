# Nexus Research Agent — Documentation

> **Status**: Active development. This documentation grows as features stabilize.  
> For quick-start instructions, see the project-level `QUICKSTART.md`.

---

## What is Nexus?

Nexus is an agentic research assistant that produces structured, citation-grounded research
summaries on any topic. It operates as a multi-agent pipeline:

```
User Query
    ↓
Planner Agent       — decomposes query into research steps
    ↓
Research Agent      — searches arxiv, web (Tavily), and knowledge base
    ↓
Writer Agent        — synthesizes findings into a structured report
    ↓
Editor Agent        — refines, formats, and optionally renders to PDF
    ↓
Output: Markdown report + optional PDF
```

## Components

| Component | Location | Description |
|---|---|---|
| Core pipeline | `src/nexus/agents/research/pipeline.py` | Orchestrates agents end-to-end |
| LLM client | `src/nexus/agents/research/llm_client.py` | Unified LLM interface (OpenAI, Anthropic) |
| Tools | `src/nexus/agents/research/tools.py` | Search tools (arxiv, Tavily, KG query) |
| Web server | `src/nexus/agents/research/server/` | FastAPI + SSE progress tracking |
| CLI | `src/nexus/cli/` | `nexus-research` command |
| Knowledge layer | `src/nexus/knowledge/` | Neo4j KG integration (in development) |

## Integration Roadmap

Nexus is being extended with a **Knowledge Graph backend** (Neo4j / AuraDB) and a
**RAG retrieval layer** to create a full-cycle R&D assistant:

```
Phase 1 (complete):   Multi-agent pipeline, web UI, PDF generation, SSE progress tracking
Phase 2 (active):     RAG retrieval — vector search over ingested papers
Phase 3 (planned):    KG integration — structured knowledge, gap detection, trend analysis
Phase 4 (vision):     Full R&D loop — ingest → query → synthesize → propose → prototype
```

## Documents in This Folder

*To be added as features stabilize:*

- `01_architecture.md` — system design and agent communication
- `02_knowledge_graph_integration.md` — Neo4j schema, Cypher queries, update flow
- `03_rag_integration.md` — embedding pipeline, retrieval strategies
- `04_research_loop.md` — automated R&D workflow design
- `05_api_reference.md` — REST API endpoints, SSE event format

## Related

- Quick start: `QUICKSTART.md`
- Source: `src/nexus/`
- KG subproject: `knowledge_graph/`
- RAG subproject: `rag/`

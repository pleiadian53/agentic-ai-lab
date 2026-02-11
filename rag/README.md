# RAG (Retrieval-Augmented Generation)

Sub-project for exploring RAG patterns, architectures, and applications within agentic AI systems.

## Overview

RAG combines information retrieval with language model generation to produce grounded, factual responses. This sub-project covers:

- **Foundational RAG** — Chunking, embedding, vector stores, retrieval, generation
- **Advanced RAG** — Reranking, hybrid search, query transformation, multi-step retrieval
- **Agentic RAG** — RAG as a tool in agentic workflows, adaptive retrieval strategies
- **Evaluation** — Retrieval quality, faithfulness, relevance metrics

## Directory Structure

```
rag/
├── __init__.py
├── README.md
├── L*/                    # Course lesson notebooks + helper scripts
│   ├── L*.ipynb
│   └── *.py
├── docs/                  # RAG-specific notes, design docs
├── examples/              # Custom RAG apps and experiments
└── environment.yml        # RAG-specific dependencies (if needed)
```

## Integration Path

Mature components will graduate to `src/nexus/` as enhancements to the Nexus Research Agent (e.g., local document retrieval, knowledge base backends) or as standalone applications.

## Related

- `notebooks/RAG/` — Scratch space for quick experiments
- `src/nexus/knowledge/` — Nexus knowledge integration point
- `tool_use/` — RAG as a retrieval tool pattern

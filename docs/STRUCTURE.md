# docs/ — Directory Structure

Visual overview of the shareable documentation space.
**Last Updated:** February 2026

---

## Directory Tree

```
docs/
├── README.md                               # 📖 Main documentation index
├── STRUCTURE.md                            # 📁 This file
├── DOCUMENTATION_GUIDES_EXAMPLE.md         # 📄 Doc structure example (reference)
│
├── installation/                           # 🔧 Setup & Environment
│   ├── ENVIRONMENT_SETUP.md
│   ├── EDITABLE_INSTALL.md
│   ├── MAMBA_VS_PIP.md
│   ├── SETUP_CHECKLIST.md
│   ├── GITHUB_SETUP.md
│   ├── INSTALL_QUICKSTART.md
│   └── SETUP_README.md
│
├── patterns/                               # 🎯 Agentic Design Patterns
│   ├── AGENTIC_PATTERNS.md
│   ├── RESEARCH_AGENT_GUIDE.md
│   └── ENHANCED_REFLECTION_PROMPT.md
│
├── workflows/                              # 🔄 Workflow Guides
│   ├── DRIVER_SCRIPT_GUIDE.md
│   └── OUTPUT_STRATEGY.md
│
├── architecture/                           # 🏗️ Project Architecture
│   ├── AGENTIC_ROADMAP.md
│   └── TEST_ORGANIZATION.md
│
├── libraries/                              # 📚 External Libraries
│   ├── README.md
│   ├── AGENT_LLM_TOOLS.md
│   ├── DATA_SCIENCE.md
│   ├── DEPENDENCIES.md
│   ├── JUPYTER.md
│   └── WEB_FRAMEWORK.md
│
├── data_management/                        # 💾 Data Organization
│   └── guidelines.md
│
├── tutorials/                              # 📖 Learning Guides
│   ├── LEARNING_GUIDE.md
│   └── USAGE_GUIDE.md
│
├── development/                            # 👨‍💻 Developer Guides
│   ├── AGENTS.md
│   ├── DOCUMENTATION_ORGANIZATION.md      # archived (Nov 2024)
│   └── DOCUMENTATION_STRUCTURE.md        # archived (Nov 2024)
│
├── RAG/                                    # 🔍 Retrieval-Augmented Generation
│   ├── ANN/
│   ├── semantic_search_beyond_text/
│   └── sentence_transformer/
│
├── knowledge_graph/                        # 🕸️ Knowledge Graphs & Neo4j
│   └── (docs from KG notebook series)
│
├── multivector_retrieval/                  # 🔢 Multi-Vector Retrieval
│   ├── README.md
│   ├── 01_multivector_text_retrieval.md
│   └── 02_clustering_in_high_dimensions.md
│
├── huggingface/                            # 🤗 HuggingFace
│   └── model_download_troubleshooting.md
│
├── responses_api/                          # 🔌 Responses API
│   └── (API reference docs)
│
├── applications/                           # 🚀 Active Applications (shareable)
│   └── nexus/
│       └── README.md                      # Nexus research agent docs
│
└── products/                              # 📦 Graduated Products (shareable)
    └── README.md
```

---

## Organization Principles

### Two Top-Level Spaces

| Space | Purpose | Audience |
|---|---|---|
| `docs/` | Shareable, publication-quality documentation | Collaborators, public |

### Within docs/: Three Layers

**Layer 1 — Topic-based** (stable cross-cutting concerns):
`installation/`, `patterns/`, `workflows/`, `architecture/`, `libraries/`,
`data_management/`, `tutorials/`, `development/`

**Layer 2 — Technology-based** (mirrors notebooks/ exploration):
`RAG/`, `knowledge_graph/`, `multivector_retrieval/`, `huggingface/`, `responses_api/`

**Layer 3 — Lifecycle-based** (application/product documentation):
`applications/<app>/`, `products/<app>/`

### Lifecycle Flow

```
docs/applications/<app>/      ← shareable docs (active)
         ↓ on graduation
docs/products/<app>/          ← shareable docs (stable)
```

---

## Adding New Documentation

| You're writing... | Put it in... |
|---|---|
| Setup or environment guide | `installation/` |
| Agentic design pattern | `patterns/` |
| Workflow walkthrough | `workflows/` |
| Project architecture/roadmap | `architecture/` |
| Library reference | `libraries/` |
| Tutorial or learning guide | `tutorials/` |
| Developer/contributor guide | `development/` |
| RAG technique notes | `RAG/<topic>/` |
| KG / Neo4j docs | `knowledge_graph/` |
| Multi-vector retrieval docs | `multivector_retrieval/` |
| Application docs (active) | `applications/<app>/` |
| Product docs (stable) | `products/<app>/` |

After adding: update `docs/README.md` in the appropriate section.

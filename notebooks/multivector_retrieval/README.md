# Image Retrieval: ColBERT and Multi-Vector Search

## Overview

This tutorial covers the key methods demonstrated in the **ColBERT multi-vector text retrieval** notebook (`colbert/L1.ipynb`). ColBERT (Contextualized Late Interaction over BERT) represents a paradigm shift in information retrieval — instead of compressing an entire document into a single vector, it retains **per-token embeddings** and uses a **late interaction** mechanism to compute fine-grained relevance scores.

This approach bridges the gap between the efficiency of dense retrieval and the effectiveness of cross-encoder rerankers.

---

## Key Concepts

### 1. Multi-Vector (Late Interaction) Embeddings

**Traditional dense retrieval** encodes a query and a document each into a **single vector**, then computes similarity (e.g., cosine) between them. This is fast but lossy — all semantic nuance is compressed into one point in vector space.

**ColBERT's approach** keeps **one embedding per token**:

```
Document: "Electric buses reduce carbon emissions by 65%"
         → [v_electric, v_buses, v_reduce, v_carbon, v_emissions, v_by, v_65, v_%]

Query:    "advantages of EV cars"
         → [v_advantages, v_of, v_EV, v_cars]
```

Each token gets its own 128-dimensional vector (for ColBERTv2), preserving fine-grained semantic information that single-vector methods discard.

**Why this matters**: A query about "EV advantages" can match strongly with the token "electric" in the document even if other tokens like "buses" don't match "cars" — the per-token matching captures partial relevance that single-vector approaches miss.

### 2. MaxSim Scoring

ColBERT's scoring mechanism is called **MaxSim** (Maximum Similarity):

```
Score(Q, D) = Σ_{q ∈ Q} max_{d ∈ D} (q · d)
```

For each query token, find the **maximum dot-product similarity** across all document tokens, then **sum** these maxima. This is the core of "late interaction" — query and document are encoded independently, but interact at scoring time through this lightweight operation.

**Step-by-step**:
1. Compute the full similarity matrix: `S[i,j] = query_token[i] · doc_token[j]`
2. For each query token (row), take the **max** across all document tokens (columns)
3. **Sum** all the per-query-token maxima → final relevance score

**Intuition**: Each query term "finds" its best-matching document term. A document is relevant if every query term has at least one strong match somewhere in the document.

### 3. Asymmetric Encoding: Query vs. Document

ColBERT uses **different encoding strategies** for queries and documents:

| Aspect | Query | Document |
|--------|-------|----------|
| **Marker token** | `QUERY_MARKER_TOKEN_ID` | `DOCUMENT_MARKER_TOKEN_ID` |
| **Embedding method** | `query_embed()` | `passage_embed()` |
| **Padding** | Padded with `[MASK]` tokens to fixed length (32 tokens) | No padding, variable length |
| **Purpose of padding** | Enables query augmentation — `[MASK]` tokens learn to represent "soft" expansion terms | Keeps storage efficient |

The `[MASK]` padding in queries is a key innovation: these tokens are not meaningless padding but learn contextual representations that act as **implicit query expansion**, helping match relevant documents even when exact terms don't appear.

### 4. Qdrant Multi-Vector Collections

The notebook demonstrates storing ColBERT embeddings in **Qdrant**, a vector database with native multi-vector support:

```python
colbert_vector_name: models.VectorParams(
    size=colbert_model.embedding_size,       # 128-dim per token
    distance=models.Distance.DOT,            # Dot product for MaxSim
    multivector_config=models.MultiVectorConfig(
        comparator=models.MultiVectorComparator.MAX_SIM,  # Native MaxSim
    ),
    hnsw_config=models.HnswConfigDiff(m=0),  # Disable HNSW (exact search)
)
```

Key design decisions:
- **DOT distance** (not cosine) — ColBERT's MaxSim uses dot product
- **MAX_SIM comparator** — Qdrant natively supports the MaxSim operation
- **HNSW disabled** — For small collections, exact search is preferred; for production, approximate search with HNSW would be enabled

### 5. Hybrid Retrieval: ColBERT + Dense

The notebook runs **both** ColBERT (multi-vector) and standard dense (single-vector, BGE-small) retrieval on the same collection, comparing results side-by-side. This demonstrates:

- **ColBERT** excels at queries requiring **token-level matching** (e.g., "search performance in Qdrant" correctly surfaces documents about MaxSim and multi-vector configurations)
- **Dense models** may rank differently because they compress all meaning into one vector
- The **same Qdrant collection** can hold both vector types, enabling hybrid retrieval strategies

---

## Helper Utilities Reference

The `colbert/helper.py` file provides several reusable utilities:

| Function | Purpose |
|----------|---------|
| `tokenize_late_interaction()` | Tokenize text with ColBERT's special marker tokens |
| `visualize_maxsim_matrix()` | Interactive heatmap of token-level similarities with MaxSim highlighting |
| `display_results_side_by_side()` | Compare two retrieval methods with duplicate detection and query highlighting |
| `pdf_to_png_screenshots()` | Convert PDF pages to images (for ColPali vision models) |
| `visualize_image_patches()` | Show how vision models divide images into patches |
| `generate_diverse_vectors()` | Create vectors with controlled cosine similarities (for testing) |
| `visualize_simhash_boundaries()` | Visualize SimHash hyperplane decision boundaries |
| `visualize_random_projection_quality()` | Show compression vs. accuracy tradeoff |
| `visualize_cluster_distribution()` | Token distribution across MUVERA clusters |
| `visualize_multivector_compression()` | Side-by-side: original multi-vector vs. MUVERA clustered |
| `aggregate_document_clusters()` | MUVERA document aggregation (AVG + fill empty clusters) |
| `aggregate_query_clusters()` | MUVERA query aggregation (SUM + zero for empty) |
| `compare_optimization_methods()` | Compare retrieval across quantization/optimization strategies |

---

## Dependencies

```
fastembed>=0.7.3          # ColBERT and dense embedding models
qdrant-client>=1.15.1     # Vector database with multi-vector support
plotly>=6.3.0             # Interactive visualizations
numpy                     # Matrix operations
colpali-engine            # Vision-language retrieval (ColPali, for advanced lessons)
pdf2image                 # PDF to image conversion
torch                     # PyTorch (CPU sufficient for inference)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ColBERT Pipeline                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Query: "advantages of EV cars"                         │
│    │                                                    │
│    ▼                                                    │
│  ┌──────────────────────┐                               │
│  │  ColBERT Encoder     │                               │
│  │  (query_embed)       │                               │
│  │  + [MASK] padding    │                               │
│  └──────┬───────────────┘                               │
│         │  [q1, q2, ..., q32]  (32 × 128-dim)          │
│         │                                               │
│         ▼                                               │
│  ┌──────────────────────────────────────────┐           │
│  │         MaxSim Scoring                    │           │
│  │                                           │           │
│  │  For each qi:                             │           │
│  │    max_j(qi · dj) ──► sum all maxima      │           │
│  │                                           │           │
│  └──────────────────────────────────────────┘           │
│         ▲                                               │
│         │  [d1, d2, ..., dN]  (N × 128-dim)            │
│  ┌──────┴───────────────┐                               │
│  │  ColBERT Encoder     │                               │
│  │  (passage_embed)     │                               │
│  │  Variable length     │                               │
│  └──────────────────────┘                               │
│    ▲                                                    │
│  Document: "Electric buses reduce carbon emissions..."  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                    Storage (Qdrant)                      │
│                                                         │
│  Collection: "colbert-tests"                            │
│  ├── Dense vectors:   BAAI/bge-small-en-v1.5 (384-dim) │
│  └── ColBERT vectors: colbert-ir/colbertv2.0 (N×128)   │
│       └── MultiVectorConfig(MAX_SIM)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## What Can We Develop Further?

### Near-Term Extensions

#### 1. ColPali: Vision-Language Retrieval
The helper file already includes utilities for **ColPali** — a vision-language model that applies ColBERT's late interaction to **document images** instead of text. This enables:
- **Direct PDF/image search** without OCR or text extraction
- Retrieval over slides, diagrams, charts, and scanned documents
- The `pdf_to_png_screenshots()` and `visualize_image_patches()` helpers are ready for this

**Next step**: Build a notebook that indexes PDF pages as images and retrieves them with natural language queries.

#### 2. MUVERA: Efficient Multi-Vector Compression
The helper file contains a full **MUVERA** (Multi-Vector Retrieval via Aggregation) implementation:
- Compresses variable-length multi-vector embeddings into **fixed-dimensional** single vectors
- Uses **SimHash** for clustering tokens, then aggregates per cluster
- Documents use **AVG** (stable), queries use **SUM** (preserves term frequency)
- Enables using standard ANN indexes (HNSW, IVF) with multi-vector quality

**Next step**: Benchmark MUVERA compression vs. raw ColBERT on retrieval quality and speed.

#### 3. Hybrid Retrieval Pipeline
Combine ColBERT with dense and sparse (BM25) retrieval in a **multi-stage pipeline**:
- **Stage 1**: Fast candidate retrieval with dense vectors or BM25
- **Stage 2**: Re-rank candidates with ColBERT's MaxSim for precision
- This is how production systems (e.g., Vespa, Qdrant) deploy ColBERT at scale

#### 4. Quantization and Optimization
The helper includes `compare_optimization_methods()` for evaluating:
- **Binary quantization** of ColBERT vectors (128× storage reduction)
- **Scalar quantization** (4× reduction with minimal quality loss)
- **Random projection** for dimensionality reduction
- Trade-off analysis between storage, speed, and retrieval quality

### Medium-Term Products

#### 5. Intelligent Document Search for Nexus
Integrate ColBERT/ColPali into the **Nexus Research Agent** for:
- Semantic search over the research paper corpus
- Image-aware retrieval (find papers by diagram/figure content)
- Fine-grained passage retrieval for citation and evidence extraction
- Multi-modal RAG: retrieve both text passages and visual content

#### 6. Research Paper Visual Search Engine
Build a standalone tool that:
- Indexes research papers as both text (ColBERT) and images (ColPali)
- Supports queries like "show me attention mechanism diagrams" or "find tables comparing model sizes"
- Provides a web UI with highlighted matching passages and image results
- Could integrate with the existing Nexus web interface (port 8004)

#### 7. Agentic Retrieval
Create an **agent that dynamically chooses retrieval strategies**:
- Use dense retrieval for broad topic queries
- Switch to ColBERT for precision-critical queries
- Use ColPali when the query implies visual content
- The agent learns which strategy works best for different query types

### Long-Term Vision

#### 8. Multi-Modal Knowledge Base
A unified retrieval system that indexes:
- Text documents (ColBERT)
- Images and PDFs (ColPali)
- Code repositories (code-specific embeddings)
- Structured data (SQL Agent integration)
- All queryable through a single natural language interface

#### 9. Self-Improving Retrieval
- Track which retrieved documents users actually use
- Fine-tune ColBERT on domain-specific relevance signals
- Implement active learning for continuous improvement
- Feed retrieval quality metrics back into the Nexus pipeline

---

## Environment Setup

This notebook series uses a **dedicated conda environment** (`image-retrieval`) separate from the project-level `agentic-ai` environment. This is because the image retrieval stack has heavy, specialized dependencies (PyTorch, transformers, ColPali git fork) that would conflict with or bloat the main environment.

Two environment files are provided:

| File | Platform | PyTorch Backend |
| ---- | -------- | --------------- |
| `environment.yml` | macOS ARM64 (local) | MPS (via conda-forge) |
| `environment-runpod.yml` | Linux x86_64 (RunPod) | CUDA (via pip) |

### macOS (Local)

```bash
cd notebooks/image_retrieval
mamba env create -f environment.yml
mamba activate image-retrieval
python -m ipykernel install --user --name image-retrieval --display-name "Python (image-retrieval)"
```

### Linux / RunPod (CUDA)

```bash
cd notebooks/image_retrieval
mamba env create -f environment-runpod.yml
mamba activate image-retrieval

# Install PyTorch with CUDA support (A40/A100 → cu121; adjust as needed)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

python -m ipykernel install --user --name image-retrieval --display-name "Python (image-retrieval)"
```

> **Why pip for CUDA PyTorch?** Mixing conda and pip PyTorch+CUDA often causes library conflicts. Installing PyTorch via pip with the `--index-url` flag is the most reliable approach on RunPod, consistent with how `genai-lab` handles this.

## Running the Notebook

```bash
# Activate the environment
mamba activate image-retrieval

# Start Qdrant (required for the vector database portions)
docker run -p 6333:6333 qdrant/qdrant

# Launch Jupyter
jupyter notebook notebooks/image_retrieval/colbert/L1.ipynb
```

> **Note**: The ColBERT model (`colbert-ir/colbertv2.0`) and dense model (`BAAI/bge-small-en-v1.5`) are downloaded automatically by `fastembed` on first use. No GPU required — CPU inference works well for these model sizes.

---

## References

- **ColBERT**: Khattab & Zaharia, "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT" (SIGIR 2020)
- **ColBERTv2**: Santhanam et al., "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction" (NAACL 2022)
- **ColPali**: Faysse et al., "ColPali: Efficient Document Retrieval with Vision Language Models" (2024)
- **MUVERA**: Lassance et al., "Multi-Vector Retrieval via Fixed Dimensional Encodings" (2024)
- **Qdrant**: [qdrant.tech](https://qdrant.tech/) — Vector database with native multi-vector support
- **fastembed**: [github.com/qdrant/fastembed](https://github.com/qdrant/fastembed) — Lightweight embedding library

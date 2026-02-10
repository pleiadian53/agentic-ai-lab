# Fastembed: Lightweight Embedding Models for Retrieval

## What is Fastembed?

[Fastembed](https://github.com/qdrant/fastembed) is a lightweight Python library by Qdrant for generating text (and image) embeddings using ONNX-optimized models. It provides a unified API for two fundamentally different embedding paradigms:

- **Dense (single-vector) embeddings** — one vector per text
- **Late interaction (multi-vector) embeddings** — one vector per token (ColBERT)

Key advantages over alternatives like `sentence-transformers`:

- **No PyTorch dependency for inference** — uses ONNX Runtime, so models run on CPU with minimal overhead
- **Automatic model download and caching** — just specify a model name
- **Consistent API** across dense, sparse, and multi-vector models
- **Small footprint** — ideal for production and edge deployment

---

## Installation

```bash
pip install fastembed>=0.7.3
```

For ColPali (vision-language) models, additional dependencies are needed:

```bash
pip install "colpali-engine[interpretability]"
```

---

## Core Concepts

### Dense Embeddings (Single-Vector)

A dense embedding model compresses an entire text into a **single fixed-dimensional vector**. This is the standard approach used by most retrieval systems.

```python
from fastembed import TextEmbedding

model = TextEmbedding("BAAI/bge-small-en-v1.5")

# Embed a single document
embedding = next(model.passage_embed(["Electric buses reduce carbon emissions."]))
print(embedding.shape)  # (384,)

# Embed a query (may use different prompt template internally)
query_emb = next(model.query_embed(["benefits of electric vehicles"]))
print(query_emb.shape)  # (384,)
```

**How it works**: The model processes the full text through a transformer, then pools all token representations (typically via CLS token or mean pooling) into one vector.

**Trade-off**: Fast and storage-efficient, but all semantic nuance is compressed into a single point. A document about "electric buses reducing emissions" and "electric cars reducing noise" gets one vector that must somehow represent both topics.

### Available Dense Models

| Model | Dimensions | Notes |
| ----- | ---------- | ----- |
| `BAAI/bge-small-en-v1.5` | 384 | Good balance of speed and quality |
| `BAAI/bge-base-en-v1.5` | 768 | Higher quality, larger |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Popular general-purpose |
| `nomic-ai/nomic-embed-text-v1.5` | 768 | Strong on benchmarks |

---

### Late Interaction Embeddings (Multi-Vector / ColBERT)

ColBERT keeps **one embedding per token**, preserving fine-grained semantic information that single-vector methods discard.

```python
from fastembed import LateInteractionTextEmbedding

model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
print(model.embedding_size)  # 128 (per-token dimension)

# Document embedding: variable number of tokens, each 128-dim
doc_emb = next(model.passage_embed(["Electric buses reduce carbon emissions by 65%."]))
print(doc_emb.shape)  # (N_tokens, 128) — e.g., (14, 128)

# model.passage_embed([...]) returns a lazy iterator that yields embeddings one passage at a time

# Query embedding: padded to fixed length (32 tokens) with [MASK]
query_emb = next(model.query_embed(["advantages of EV cars"]))
print(query_emb.shape)  # (32, 128)
```

**How it works**: Each token in the text gets its own 128-dimensional vector. The model encodes query and document independently (enabling pre-computation of document embeddings), but they interact at scoring time through **MaxSim**.

### Asymmetric Encoding

ColBERT encodes queries and documents differently:

```
Document: [CLS] [D] electric buses reduce ... [SEP]
  → Variable-length output (one vector per actual token)

Query:    [CLS] [Q] advantages of EV cars [MASK] [MASK] ... [MASK]
  → Fixed-length output (padded to 32 tokens)
```

| Aspect | Query | Document |
| ------ | ----- | -------- |
| **Method** | `query_embed()` | `passage_embed()` |
| **Marker** | `[Q]` token after `[CLS]` | `[D]` token after `[CLS]` |
| **Length** | Fixed (32 tokens, padded with `[MASK]`) | Variable (actual token count) |
| **`[MASK]` role** | Learns contextual "soft expansion" terms | Not used |

The `[MASK]` padding is not meaningless — these tokens learn to represent implicit query expansion terms, helping match relevant documents even when exact terms are absent.

---

## MaxSim Scoring

The core scoring mechanism that makes ColBERT work:

```python
import numpy as np

# Compute full similarity matrix
similarity_matrix = np.dot(query_embeddings, document_embeddings.T)
# Shape: (n_query_tokens, n_doc_tokens)

# MaxSim: for each query token, find best-matching document token, then sum
score = similarity_matrix.max(axis=1).sum()
```

**Formula**:

```
Score(Q, D) = Σ_{q ∈ Q}  max_{d ∈ D}  (q · d)
```

**Intuition**: Each query term independently "finds" its best match in the document. A document is relevant if every query term has at least one strong match somewhere.

### Why MaxSim Beats Single-Vector

Consider the query `"advantages of EV cars"` against a document about `"electric buses reducing emissions"`:

- **Dense model**: The single query vector must be close to the single document vector in 384-dim space. "Cars" vs "buses" pulls them apart.
- **ColBERT**: The token `"EV"` matches strongly with `"electric"`. The token `"advantages"` matches with `"benefits"` or `"reduce"`. Each match is captured independently. The sum of these partial matches yields a high score.

### Visualizing MaxSim

```python
from helper import visualize_maxsim_matrix

fig = visualize_maxsim_matrix(
    similarity_matrix,
    query_tokens=query_tokens,
    document_tokens=document_tokens,
    width=600,
)
fig.show()
```

This produces a heatmap where:
- **X-axis**: query tokens
- **Y-axis**: document tokens
- **Red borders**: the maximum similarity cell for each query token (the MaxSim selections)
- **Color intensity**: similarity strength

---

## Batch Processing

Both model types support batch embedding:

```python
# Dense: batch embed multiple documents
documents = ["doc1...", "doc2...", "doc3..."]
embeddings = list(model.passage_embed(documents))
# Returns list of (384,) arrays

# ColBERT: batch embed
embeddings = list(colbert_model.passage_embed(documents))
# Returns list of (N_i, 128) arrays (variable length per document)
```

Fastembed handles batching internally for efficiency. For large corpora, embeddings are generated lazily (via generators) to manage memory.

---

## Tokenization Internals

To inspect how ColBERT tokenizes text (useful for debugging and visualization):

```python
from helper import tokenize_late_interaction

# Document tokenization (includes [CLS], [D] marker, actual tokens, [SEP])
doc_tokens = tokenize_late_interaction(model, "Electric buses reduce emissions.", is_doc=True)
# ['[CLS]', '[D]', 'electric', 'buses', 'reduce', 'emissions', '.', '[SEP]']

# Query tokenization (includes [CLS], [Q] marker, tokens — [MASK] filtered by default)
query_tokens = tokenize_late_interaction(model, "EV advantages", is_doc=False)
# ['[CLS]', '[Q]', 'ev', 'advantages']
```

The `tokenize_late_interaction()` helper in `helper.py`:
1. Tokenizes using the model's internal tokenizer
2. Inserts the appropriate marker token (`[D]` or `[Q]`) after `[CLS]`
3. Filters out tokens in the model's skip list (punctuation, etc.)
4. Converts token IDs back to readable strings

---

## Applications

### 1. Semantic Search

The most direct application. Index a corpus with ColBERT embeddings, then retrieve documents matching a natural language query.

**When to use ColBERT over dense**:
- Queries where **partial term matching** matters (e.g., technical search)
- Domains with **specialized vocabulary** where exact token matches are important
- When you need **interpretable** retrieval (the MaxSim matrix shows exactly why a document matched)

### 2. Retrieval-Augmented Generation (RAG)

Use ColBERT as the retriever in a RAG pipeline:
- **Stage 1**: Retrieve top-k passages with ColBERT's fine-grained matching
- **Stage 2**: Feed retrieved passages to an LLM for answer generation

ColBERT's token-level matching is especially valuable for RAG because it retrieves passages with precise term overlap, reducing hallucination.

### 3. Re-ranking

Use dense retrieval for fast candidate generation (top-100), then re-rank with ColBERT for precision (top-10). This is the standard production pattern:

```python
# Stage 1: Fast dense retrieval
candidates = dense_query("search performance in Qdrant", limit=100)

# Stage 2: Re-rank with ColBERT
reranked = colbert_query("search performance in Qdrant", limit=10)
```

### 4. Duplicate Detection

ColBERT's token-level similarity matrix reveals whether two documents share specific concepts, not just overall topic similarity. This is useful for:
- Near-duplicate detection in document corpora
- Plagiarism detection
- Citation recommendation (finding papers that discuss the same specific concepts)

### 5. Cross-Lingual Retrieval

Multilingual ColBERT variants can match queries in one language against documents in another, with token-level alignment showing which terms correspond across languages.

### 6. Research Paper Search (Nexus Integration)

For the Nexus research platform, ColBERT enables:
- Fine-grained passage retrieval for evidence extraction
- Matching specific technical terms across papers
- Interpretable search results (show users *why* a paper matched)

---

## Performance Characteristics

| Metric | Dense (BGE-small) | ColBERT v2 |
| ------ | ------------------ | ---------- |
| **Embedding dim** | 384 (single vector) | 128 × N tokens |
| **Storage per doc** | ~1.5 KB | ~5-50 KB (depends on length) |
| **Embedding speed** | ~1ms/doc | ~5ms/doc |
| **Query speed** | Sub-millisecond (ANN) | Slower (multi-vector comparison) |
| **Retrieval quality** | Good | Better (especially for specific queries) |
| **Interpretability** | Low (single score) | High (per-token similarity matrix) |

**Rule of thumb**: Use dense for speed-critical applications with broad queries. Use ColBERT when precision and interpretability matter more than latency.

---

## References

- **ColBERT**: Khattab & Zaharia, "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT" (SIGIR 2020)
- **ColBERTv2**: Santhanam et al., "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction" (NAACL 2022)
- **Fastembed**: [github.com/qdrant/fastembed](https://github.com/qdrant/fastembed)
- **BGE Models**: Xiao et al., "C-Pack: Packaged Resources To Advance General Chinese Embedding" (2023)

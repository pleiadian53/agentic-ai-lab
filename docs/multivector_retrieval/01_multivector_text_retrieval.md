# Prerequisites for Multi-Vector Retrieval

> **Series**: Multi-Vector Image Retrieval
> **Part**: 01 — Foundations
> **Next**: [L1 Notebook — ColBERT Multi-Vector Text Retrieval](../../notebooks/image_retrieval/colbert/L1.ipynb)

This document covers the foundational concepts needed before diving into the hands-on ColBERT notebook. The ideas span geometry, algorithms, and systems design — the machinery behind modern retrieval and RAG-style models. They form a coherent mental model rather than isolated definitions, because they only make sense together.

---

## 1. Dense Embedding Vectors: Turning Meaning into Geometry

A **dense embedding** is a learned function that maps objects into a continuous vector space:

$$
f : \text{object} \rightarrow \mathbb{R}^d
$$

The object might be an image, a sentence, a protein sequence, or a medical code trajectory. What matters is the output: a $d$-dimensional vector where geometric relationships encode semantic relationships.

Key properties:

- **Dense** — most dimensions are non-zero (unlike bag-of-words or TF-IDF representations)
- **Semantic locality** — similar objects land near each other in vector space
- **Learned geometry** — the axes themselves have no human-interpretable meaning; only distances and angles matter

The embedding model varies by domain: CNNs or Vision Transformers (ViT) for images, transformer encoders for text, and sequence models like DNABERT or Evo-style encoders for biological sequences.

> An embedding is not a label. It is a *coordinate system where similarity becomes distance*.

This is why retrieval becomes a geometric problem instead of a symbolic one.

---

## 2. Vector Similarity: Measuring "Nearness"

Once everything lives in $\mathbb{R}^d$, retrieval reduces to a **similarity function**. Three dominate in practice:

### Cosine Similarity

$$
\text{cos}(\mathbf{x}, \mathbf{y}) = \frac{\mathbf{x} \cdot \mathbf{y}}{\|\mathbf{x}\| \, \|\mathbf{y}\|}
$$

- Measures the **angle** between vectors, ignoring magnitude
- Invariant to scaling — a vector and its scaled version are equally similar to any third vector
- Dominant in embedding models trained with contrastive loss (CLIP, Sentence-BERT)

### Dot Product

$$
\mathbf{x} \cdot \mathbf{y} = \sum_{i=1}^{d} x_i \, y_i
$$

- Equivalent to cosine similarity when vectors are $\ell_2$-normalized
- Often used directly for speed (avoids the normalization division)
- Used by ColBERT's MaxSim scoring

### Euclidean Distance

$$
\|\mathbf{x} - \mathbf{y}\|_2 = \sqrt{\sum_{i=1}^{d} (x_i - y_i)^2}
$$

- Sensitive to vector magnitude
- Less common in modern embedding systems unless the model is explicitly trained for it

A key geometric fact about high-dimensional spaces:

> In high dimensions, angles are often more stable than distances.

As dimensionality grows, pairwise Euclidean distances concentrate around a narrow band, making them less discriminative. Cosine similarity, which depends only on angle, remains informative. This is why cosine similarity is the default choice in most embedding-based retrieval systems. This same phenomenon explains why standard k-means (which uses Euclidean distance) degrades in high dimensions — see [02 — Clustering in High-Dimensional Spaces](./02_clustering_in_high_dimensions.md) for a deep dive into cosine-based clustering, recommended algorithms, and dimensionality reduction strategies.

---

## 3. Nearest Neighbor Search: The Exact Version

Given a query vector $\mathbf{q}$ and a database of $N$ vectors $\{\mathbf{x}_1, \dots, \mathbf{x}_N\}$, exact nearest neighbor search finds:

$$
\arg\max_{i} \; \text{sim}(\mathbf{q}, \mathbf{x}_i)
$$

The computational cost is $O(Nd)$ per query — a linear scan over all vectors, computing similarity for each. This is perfectly fine for $N = 10^4$ but becomes prohibitive at $N = 10^8$.

This is where theory meets hardware reality: exact search does not scale, and practical systems must trade exactness for speed.

---

## 4. Approximate Nearest Neighbor (ANN) Search

**ANN search** deliberately sacrifices exactness for speed, memory efficiency, and scalability. The core idea:

> Return a point that is *very close* to the true nearest neighbor, with high probability.

The question shifts from *"What is the closest vector?"* to *"What is close enough, fast enough?"*

This is not a hack — it is a design philosophy baked into every modern retrieval system. The key insight is that for most applications (search, RAG, recommendation), returning the 2nd or 5th nearest neighbor instead of the 1st has negligible impact on downstream quality, while reducing latency by orders of magnitude.

---

## 5. Why ANN Is Hard in High Dimensions

Two phenomena make high-dimensional nearest neighbor search fundamentally difficult:

**Distance concentration.** In high-dimensional spaces, pairwise distances cluster tightly around a mean value. The ratio between the nearest and farthest neighbor distances approaches 1, making it hard to distinguish "close" from "far."

**Indexing collapse.** Classical spatial data structures — KD-trees, ball trees, R-trees — rely on recursively partitioning space. Beyond roughly 20–30 dimensions, the partitions stop providing useful pruning, and search degenerates to a linear scan.

These curses motivate a different approach: instead of partitioning space, build a **graph** that encodes local connectivity and navigate it greedily.

---

## 6. HNSW: Hierarchical Navigable Small World Graphs

**HNSW** (Hierarchical Navigable Small World) is the dominant ANN index used by Qdrant, FAISS, Milvus, Weaviate, and most production vector databases.

The core idea is a **multi-layer graph** where edges connect nearby vectors, enabling fast greedy navigation from any starting point to the neighborhood of a query.

### Structure

- **Top layers** — sparse graphs with long-range connections (coarse navigation)
- **Bottom layer** — a dense graph capturing fine-grained local neighborhoods
- Inspired by small-world networks: short average path lengths combined with high local clustering

### Search Algorithm

1. Enter the graph at the top layer through a fixed entry point
2. Greedily traverse edges toward neighbors closer to the query vector
3. When no closer neighbor exists at the current layer, drop down one layer
4. Repeat until reaching the bottom layer
5. Perform a broader local search at the bottom layer to refine the result set

This is essentially **hill-climbing in vector space**, augmented with hierarchical shortcuts that prevent getting stuck in local optima.

### Why HNSW Works Well

- **Near-logarithmic search complexity** — the hierarchical structure provides $O(\log N)$-like scaling
- **Excellent recall–latency tradeoff** — tunable via search parameters
- **Incremental insertion** — new vectors can be added without rebuilding the index
- **Robust to high dimensionality** — graph connectivity adapts to the intrinsic structure of the data

### Key Parameters

| Parameter | Controls | Tradeoff |
| --------- | -------- | -------- |
| **M** | Neighbors per node | Graph density vs. memory |
| **ef_search** | Search beam width | Recall vs. query latency |
| **ef_construction** | Build-time beam width | Index quality vs. build time |

In Qdrant, setting `m=0` disables HNSW entirely (exact search), which is appropriate for small collections or when multi-vector scoring is used as a re-ranker.

---

## 7. From Single-Vector to Multi-Vector Retrieval

With these foundations in place, the motivation for multi-vector retrieval becomes clear.

In **single-vector retrieval**, each object (document, image) is represented by one embedding vector. Similarity is a single number: $\text{sim}(\mathbf{q}, \mathbf{d})$. This is fast and simple, but compresses all semantic content into a single point — a lossy operation.

In **multi-vector retrieval**, each object produces *multiple* embedding vectors:

- A text document → one vector per token (ColBERT)
- An image → one vector per patch (ColPali)
- A PDF page → one vector per visual region

Similarity aggregation becomes the central design choice:

| Strategy | Formula | Used By |
| -------- | ------- | ------- |
| **MaxSim** | $\sum_{q \in Q} \max_{d \in D} (\mathbf{q} \cdot \mathbf{d})$ | ColBERT, ColPali |
| **Sum** | $\sum_{q \in Q} \sum_{d \in D} (\mathbf{q} \cdot \mathbf{d})$ | Some cross-encoders |
| **Learned pooling** | Neural aggregation over token similarities | Poly-encoders |

**MaxSim** — the strategy used by ColBERT — finds the best-matching document token for each query token, then sums these maxima. This preserves fine-grained term-level matching that single-vector approaches discard.

ANN indexing (HNSW) becomes even more critical in the multi-vector setting because the total number of vectors explodes: a corpus of 1M documents with 100 tokens each produces 100M individual vectors. Efficient approximate search over this space is essential.

The connection to attention mechanisms is worth noting: multi-vector retrieval is structurally similar to cross-attention, but externalized into a pre-built index rather than computed on-the-fly. The query tokens attend to document tokens through the similarity matrix, and MaxSim acts as a hard attention aggregation.

---

## 8. The Retrieval Pipeline: A Unified View

The complete retrieval pipeline chains four components:

$$
\text{Embedding Model} \xrightarrow{\text{encode}} \text{Vector Space} \xrightarrow{\text{index}} \text{ANN Structure} \xrightarrow{\text{query}} \text{Retrieved Results}
$$

1. **Embedding model** — learns a semantic geometry where meaningful similarity corresponds to vector proximity
2. **Similarity function** — defines what "meaningfully close" means (cosine, dot product, MaxSim)
3. **ANN index (HNSW)** — builds navigational shortcuts through that geometry for sub-linear search
4. **Retrieval** — fast, approximate reasoning over learned space

This architecture is not specific to text or images. The same spine underlies RAG pipelines, protein structure search, EHR retrieval, genomic sequence matching, and recommendation systems. The embedding model and similarity function change; the indexing and retrieval machinery stays the same.

---

## Next Steps

The [L1 notebook](../../notebooks/image_retrieval/colbert/L1.ipynb) puts these concepts into practice:

- **Section 1–3**: Load ColBERT via fastembed, embed documents and queries as multi-vectors, compute the MaxSim similarity matrix
- **Section 4–5**: Set up a Qdrant collection with both dense and ColBERT vector fields, demonstrating the named multi-vector configuration
- **Section 6–7**: Compare ColBERT (multi-vector) vs. dense (single-vector) retrieval results side-by-side, visualize the token-level similarity matrix

For deeper dives into the libraries used:

- [Fastembed Tutorial](../../notebooks/image_retrieval/colbert/docs/fastembed_tutorial.md) — embedding models, ColBERT internals, MaxSim scoring
- [Qdrant Tutorial](../../notebooks/image_retrieval/colbert/docs/qdrant_tutorial.md) — vector database setup, multi-vector collections, hybrid retrieval patterns

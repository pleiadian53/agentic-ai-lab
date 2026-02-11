# Qdrant: Vector Database for Multi-Vector Retrieval

## What is Qdrant?

[Qdrant](https://qdrant.tech/) is an open-source vector database purpose-built for similarity search. Unlike general-purpose databases that bolt on vector support as an afterthought, Qdrant is designed from the ground up for high-dimensional vector operations with features that matter for modern retrieval:

- **Native multi-vector support** — store and query ColBERT-style per-token embeddings directly
- **Multiple named vectors per point** — combine dense, sparse, and multi-vector representations in a single collection
- **MaxSim comparator** — built-in late interaction scoring without custom application logic
- **Payload filtering** — combine vector similarity with metadata filters
- **Quantization** — binary, scalar, and product quantization for storage/speed trade-offs
- **Horizontal scaling** — sharding and replication for production workloads

---

## Installation and Setup

### Python Client

```bash
pip install qdrant-client>=1.15.1
```

### Running Qdrant

**Docker** (recommended for local development):

```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

- Port **6333**: REST API
- Port **6334**: gRPC API (faster for bulk operations)

**In-memory** (no server needed, good for testing):

```python
from qdrant_client import QdrantClient

client = QdrantClient(":memory:")  # Ephemeral, data lost on exit
```

**Persistent local storage** (no Docker):

```python
client = QdrantClient(path="./qdrant_data")  # Stores to disk
```

**Remote server**:

```python
client = QdrantClient("http://localhost:6333")
# Or with API key for cloud:
# client = QdrantClient("https://your-cluster.qdrant.io", api_key="...")
```

---

## Core Concepts

### Collections

A collection is a named set of points (vectors + payloads). Each collection defines its vector configuration at creation time.

```python
from qdrant_client import QdrantClient, models

client = QdrantClient("http://localhost:6333")

# Simple collection with one vector type
client.create_collection(
    "my_collection",
    vectors_config=models.VectorParams(
        size=384,                        # Vector dimensionality
        distance=models.Distance.COSINE, # Similarity metric
    ),
)
```

### Points

A point is the fundamental unit in Qdrant — it contains:

- **ID** — unique identifier (integer or UUID)
- **Vector(s)** — one or more named embedding vectors
- **Payload** — arbitrary JSON metadata (filterable)

```python
client.upsert(
    "my_collection",
    points=[
        models.PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],           # 384-dim vector
            payload={"text": "document content", "source": "arxiv", "year": 2024},
        ),
    ],
)
```

### Distance Metrics

| Metric | Formula | Use Case |
| ------ | ------- | -------- |
| `COSINE` | 1 - cos(a, b) | General text similarity (normalized vectors) |
| `DOT` | a · b | ColBERT MaxSim, when magnitude matters |
| `EUCLID` | \|\|a - b\|\| | Spatial/geometric similarity |
| `MANHATTAN` | Σ\|a_i - b_i\| | Sparse or discrete features |

**For ColBERT, always use `DOT`** — MaxSim relies on dot product, not cosine.

---

## Multi-Vector Collections (ColBERT)

This is Qdrant's killer feature for late interaction models. A single collection can hold both dense and multi-vector representations:

```python
collection_name = "colbert-tests"
dense_vector_name = "BAAI-bge-small-en-v1.5"
colbert_vector_name = "colbert-ir-colbertv2.0"

client.create_collection(
    collection_name,
    vectors_config={
        # Standard dense vector
        dense_vector_name: models.VectorParams(
            size=384,                        # Single 384-dim vector
            distance=models.Distance.COSINE,
        ),
        # ColBERT multi-vector
        colbert_vector_name: models.VectorParams(
            size=128,                        # Per-token dimension
            distance=models.Distance.DOT,    # MaxSim uses dot product
            multivector_config=models.MultiVectorConfig(
                comparator=models.MultiVectorComparator.MAX_SIM,
            ),
            hnsw_config=models.HnswConfigDiff(m=0),  # See note below
        ),
    },
)
```

### Key Configuration Details

**`multivector_config`**: Tells Qdrant that this vector field stores a *matrix* (N tokens × 128 dims) rather than a single vector. The `MAX_SIM` comparator implements ColBERT's scoring natively:

```
Score(Q, D) = Σ_{q ∈ Q}  max_{d ∈ D}  (q · d)
```

**`hnsw_config=HnswConfigDiff(m=0)`**: Disables the HNSW approximate nearest neighbor index for this vector. For small collections or when using multi-vector as a re-ranker, exact search is preferred. For large-scale deployment, you would enable HNSW or use quantization.

### Inserting Multi-Vector Data

```python
from fastembed import LateInteractionTextEmbedding, TextEmbedding

colbert_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
dense_model = TextEmbedding("BAAI/bge-small-en-v1.5")

documents = [
    "Qdrant is a vector database designed for similarity search",
    "SQL databases use structured tables with predefined schemas",
    "Qdrant supports multi-vector configurations for ColBERT",
]

client.upsert(
    collection_name,
    points=[
        models.PointStruct(
            id=i,
            vector={
                dense_vector_name: next(dense_model.passage_embed([doc])),
                colbert_vector_name: next(colbert_model.passage_embed([doc])),
            },
            payload={"text": doc},
        )
        for i, doc in enumerate(documents, start=1)
    ],
)
```

Each point now stores:
- One 384-dim dense vector
- One N×128 multi-vector matrix (where N varies per document)

---

## Querying

### Basic Query

```python
# Dense query
results = client.query_points(
    collection_name,
    query=next(dense_model.query_embed(["search performance"])),
    using=dense_vector_name,   # Which named vector to search
    limit=5,
    with_payload=True,
)

for point in results.points:
    print(f"Score: {point.score:.4f} | {point.payload['text']}")
```

### ColBERT Multi-Vector Query

```python
# ColBERT query — same API, Qdrant handles MaxSim internally
results = client.query_points(
    collection_name,
    query=next(colbert_model.query_embed(["search performance"])),
    using=colbert_vector_name,
    limit=5,
    with_payload=True,
)
```

The `using` parameter selects which named vector to search against. Qdrant automatically applies the configured comparator (MaxSim for multi-vectors, standard ANN for dense).

### Payload Filtering

Combine vector similarity with metadata filters:

```python
results = client.query_points(
    collection_name,
    query=query_embedding,
    using=dense_vector_name,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="source",
                match=models.MatchValue(value="arxiv"),
            ),
            models.FieldCondition(
                key="year",
                range=models.Range(gte=2023),
            ),
        ]
    ),
    limit=10,
)
```

Filter types include:
- **`MatchValue`** — exact match
- **`MatchAny`** — match any value in a list
- **`Range`** — numeric range (gte, lte, gt, lt)
- **`MatchText`** — full-text substring match
- **`HasId`** — filter by point IDs
- **`IsEmpty` / `IsNull`** — check for missing fields

---

## Hybrid Retrieval Patterns

### Pattern 1: Dense + ColBERT in One Collection

Store both representations and query each independently:

```python
import time

def colbert_query(q: str, limit: int = 5) -> list[dict]:
    start = time.monotonic()
    embedding = next(colbert_model.query_embed(q))
    print(f"ColBERT embed: {time.monotonic() - start:.3f}s")

    start = time.monotonic()
    result = client.query_points(
        collection_name,
        query=embedding,
        using=colbert_vector_name,
        limit=limit,
        with_payload=True,
    )
    print(f"ColBERT search: {time.monotonic() - start:.3f}s")
    return [point.payload for point in result.points]

def dense_query(q: str, limit: int = 5) -> list[dict]:
    start = time.monotonic()
    embedding = next(dense_model.query_embed(q))
    print(f"Dense embed: {time.monotonic() - start:.3f}s")

    start = time.monotonic()
    result = client.query_points(
        collection_name,
        query=embedding,
        using=dense_vector_name,
        limit=limit,
        with_payload=True,
    )
    print(f"Dense search: {time.monotonic() - start:.3f}s")
    return [point.payload for point in result.points]
```

### Pattern 2: Two-Stage Retrieval (Retrieve + Re-rank)

Use dense for fast candidate generation, then re-rank with ColBERT:

```python
# Stage 1: Fast dense retrieval (top-100 candidates)
candidates = client.query_points(
    collection_name,
    query=next(dense_model.query_embed(["your query"])),
    using=dense_vector_name,
    limit=100,
)
candidate_ids = [p.id for p in candidates.points]

# Stage 2: Re-rank candidates with ColBERT
reranked = client.query_points(
    collection_name,
    query=next(colbert_model.query_embed(["your query"])),
    using=colbert_vector_name,
    query_filter=models.Filter(
        must=[models.HasIdCondition(has_id=candidate_ids)]
    ),
    limit=10,
)
```

### Pattern 3: Reciprocal Rank Fusion

Combine rankings from multiple vector types:

```python
from qdrant_client import models

# Qdrant supports prefetch + fusion natively
results = client.query_points(
    collection_name,
    prefetch=[
        models.Prefetch(
            query=next(dense_model.query_embed(["your query"])),
            using=dense_vector_name,
            limit=50,
        ),
        models.Prefetch(
            query=next(colbert_model.query_embed(["your query"])),
            using=colbert_vector_name,
            limit=50,
        ),
    ],
    query=models.FusionQuery(fusion=models.Fusion.RRF),  # Reciprocal Rank Fusion
    limit=10,
)
```

---

## Quantization and Optimization

For production workloads, Qdrant offers several optimization strategies:

### Binary Quantization

Reduces each float32 dimension to a single bit — **128× storage reduction**:

```python
client.update_collection(
    collection_name,
    quantization_config=models.BinaryQuantization(
        binary=models.BinaryQuantizationConfig(always_ram=True),
    ),
)
```

### Scalar Quantization

Reduces float32 to int8 — **4× storage reduction** with minimal quality loss:

```python
client.update_collection(
    collection_name,
    quantization_config=models.ScalarQuantization(
        scalar=models.ScalarQuantizationConfig(
            type=models.ScalarType.INT8,
            quantile=0.99,
            always_ram=True,
        ),
    ),
)
```

### Search with Quantization

```python
results = client.query_points(
    collection_name,
    query=query_embedding,
    using=dense_vector_name,
    search_params=models.SearchParams(
        quantization=models.QuantizationSearchParams(
            rescore=True,   # Re-score top results with original vectors
            oversampling=2.0,  # Retrieve 2x candidates before rescoring
        ),
    ),
    limit=10,
)
```

---

## Collection Management

### Inspect Collection

```python
info = client.get_collection(collection_name)
print(f"Points: {info.points_count}")
print(f"Vectors: {info.vectors_count}")
print(f"Status: {info.status}")
```

### Delete Collection

```python
client.delete_collection(collection_name)
```

### Delete Points

```python
# By ID
client.delete(collection_name, points_selector=models.PointIdsList(points=[1, 2, 3]))

# By filter
client.delete(
    collection_name,
    points_selector=models.FilterSelector(
        filter=models.Filter(
            must=[models.FieldCondition(key="source", match=models.MatchValue(value="old"))]
        )
    ),
)
```

### Create Payload Index (for faster filtering)

```python
client.create_payload_index(
    collection_name,
    field_name="source",
    field_schema=models.PayloadSchemaType.KEYWORD,
)
```

---

## Applications

### 1. Semantic Document Search

The most direct use case. Index documents with dense and/or ColBERT vectors, retrieve by natural language query.

**Best for**: Knowledge bases, FAQ systems, documentation search, internal tooling.

### 2. RAG (Retrieval-Augmented Generation)

Qdrant as the retrieval backend for LLM-powered question answering:

- Index document chunks with embeddings
- Retrieve relevant chunks for a user query
- Feed chunks as context to an LLM
- ColBERT's precision reduces hallucination by retrieving more relevant passages

### 3. Research Paper Discovery (Nexus Integration)

For the Nexus research platform:

- **Multi-vector paper index**: Store ColBERT embeddings for fine-grained passage matching
- **Metadata filtering**: Filter by year, venue, author, domain
- **Hybrid search**: Dense for broad topic discovery + ColBERT for specific concept matching
- **Citation graphs**: Store citation relationships as payload, combine with vector similarity

### 4. Image Retrieval (ColPali)

Qdrant's multi-vector support extends naturally to vision-language models:

- Index PDF pages as ColPali multi-vector embeddings
- Query with natural language to find specific figures, tables, or diagrams
- No OCR needed — the model "sees" the page directly

### 5. Recommendation Systems

- Store user and item embeddings
- Use payload filters for business rules (availability, region, category)
- Combine collaborative filtering vectors with content-based vectors in named vector fields

### 6. Anomaly Detection

- Index normal behavior embeddings
- Query new observations — low similarity scores indicate anomalies
- Payload filters for time windows, device types, etc.

### 7. Multi-Tenant Applications

Qdrant supports efficient multi-tenancy via payload filtering:

```python
# Insert with tenant ID
client.upsert("shared_collection", points=[
    models.PointStruct(
        id=1,
        vector=embedding,
        payload={"tenant_id": "customer_A", "text": "..."},
    ),
])

# Query scoped to tenant
results = client.query_points(
    "shared_collection",
    query=query_embedding,
    query_filter=models.Filter(
        must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value="customer_A"))]
    ),
    limit=10,
)
```

---

## Qdrant vs. Alternatives

| Feature | Qdrant | Pinecone | Weaviate | Milvus |
| ------- | ------ | -------- | -------- | ------ |
| **Multi-vector (ColBERT)** | Native MaxSim | No | No | Limited |
| **Named vectors** | Yes (multiple per point) | No | No | Yes |
| **Quantization** | Binary, Scalar, PQ | Yes | Yes | Yes |
| **Payload filtering** | Rich (nested, geo, text) | Basic | GraphQL | Basic |
| **Deployment** | Docker, Cloud, Embedded | Cloud only | Docker, Cloud | Docker, Cloud |
| **License** | Apache 2.0 | Proprietary | BSD-3 | Apache 2.0 |
| **Language** | Rust | — | Go | Go/C++ |

Qdrant's native multi-vector support with MaxSim is its primary differentiator — no other major vector database supports ColBERT-style late interaction scoring out of the box.

---

## Production Considerations

### Indexing Strategy

- **Small collections (<100K points)**: Exact search is fine, disable HNSW (`m=0`)
- **Medium (100K–10M)**: Enable HNSW with default parameters
- **Large (>10M)**: Use quantization + HNSW, consider sharding

### Memory vs. Disk

```python
# Force vectors to stay on disk (saves RAM for large collections)
client.update_collection(
    collection_name,
    optimizer_config=models.OptimizersConfigDiff(memmap_threshold=10000),
)
```

### Snapshots and Backups

```python
# Create snapshot
client.create_snapshot(collection_name)

# List snapshots
snapshots = client.list_snapshots(collection_name)
```

---

## References

- **Qdrant Documentation**: [qdrant.tech/documentation](https://qdrant.tech/documentation/)
- **Qdrant Python Client**: [github.com/qdrant/qdrant-client](https://github.com/qdrant/qdrant-client)
- **Multi-Vector Tutorial**: [qdrant.tech/articles/late-interaction-models](https://qdrant.tech/articles/late-interaction-models/)
- **Quantization Guide**: [qdrant.tech/documentation/guides/quantization](https://qdrant.tech/documentation/guides/quantization/)
- **ColBERT + Qdrant**: Demonstrated in `L1.ipynb` / `L1.py` in this directory

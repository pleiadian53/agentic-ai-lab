# Navigable Small World and HNSW: Graph-Based Approximate Nearest Neighbor Search

**How a simple idea from network science -- "six degrees of separation" -- powers the fastest vector search algorithms in production today.**

Next: [Part 2 -- How Proximity Graphs Are Actually Constructed](./02_proximity_graph_construction.md)

---

## 1. The Problem: Finding Nearest Neighbors at Scale

Given a query vector $\mathbf{q} \in \mathbb{R}^d$ and a database of $N$ vectors $\{\mathbf{v}_1, \dots, \mathbf{v}_N\}$, find the $k$ vectors closest to $\mathbf{q}$ under some distance metric (cosine, Euclidean, inner product).

**Brute-force** computes all $N$ distances and returns the top $k$:

$$
\text{Time: } O(Nd), \quad \text{Space: } O(Nd)
$$

This is exact but unacceptable for large $N$. At $N = 10^9$ vectors in $d = 768$ dimensions, a single query would require approximately $10^{12}$ floating-point operations.

**Approximate Nearest Neighbor (ANN)** algorithms trade a small amount of accuracy for dramatic speedups. The key insight: we don't need the *exact* nearest neighbors -- we need *very good* neighbors, *very fast*.

Among ANN methods, **graph-based approaches** (NSW, HNSW) consistently achieve the best recall-vs-speed tradeoffs in benchmarks. They are the default index type in most vector databases (Weaviate, Milvus, Qdrant, Pinecone).

---

## 2. The Core Idea: Search as Graph Navigation

Instead of scanning all vectors, we build a **proximity graph** -- a graph where:

- Each vector is a **node**
- Each node is connected by **edges** to its approximate nearest neighbors

To answer a query, we **navigate the graph**: start at some entry point, move to the neighbor closest to the query, repeat until we can't improve. This is **greedy search** on a graph.

The critical question is: *what graph structure makes greedy search work well?*

---

## 3. Navigable Small World (NSW)

### 3.1 Small-World Networks

The term "small world" comes from network science (Watts and Strogatz, 1998). A small-world network has two properties:

1. **High clustering**: neighbors of a node tend to be neighbors of each other (local structure)
2. **Short average path length**: any two nodes can be reached in $O(\log N)$ hops (global connectivity)

Social networks are the classic example: your friends know each other (clustering), but you can reach anyone on Earth through approximately 6 intermediaries (short paths).

### 3.2 Why Small-World Structure Helps Search

If we build a proximity graph with small-world properties, greedy search becomes efficient:

- **Short-range edges** (connections to nearby vectors) enable fine-grained local navigation -- once we're in the right neighborhood, we can quickly find the nearest neighbor.
- **Long-range edges** (connections to distant vectors) enable fast traversal across the space -- we can jump from one region to another without traversing every intermediate node.

Without long-range edges, greedy search gets trapped in local regions. Without short-range edges, it can't do precise local search. The combination is what makes NSW work.

### 3.3 The NSW Search Algorithm

Given a query $\mathbf{q}$ and an entry point node $v_{\text{entry}}$:

```text
SEARCH_NSW(q, entry_point, num_results):
    candidates = priority_queue([entry_point])    # min-heap by distance to q
    visited = set([entry_point])
    results = priority_queue([entry_point])        # max-heap, keeps closest k

    while candidates is not empty:
        c = candidates.pop_closest()

        # Stopping condition: closest candidate is farther than worst result
        if dist(c, q) > dist(results.farthest(), q):
            break

        for neighbor in c.edges:
            if neighbor not in visited:
                visited.add(neighbor)
                if dist(neighbor, q) < dist(results.farthest(), q):
                    candidates.add(neighbor)
                    results.add(neighbor)
                    if len(results) > num_results:
                        results.remove_farthest()

    return results
```

This is a **beam search** on the graph: we maintain a frontier of candidates and greedily expand the most promising ones. The search terminates when no candidate is closer to the query than the worst current result.

### 3.4 NSW Construction (Incremental Insertion)

The graph is built by inserting vectors **one at a time**. For each new vector $\mathbf{v}_{\text{new}}$:

1. **Search** the current graph for the $M$ approximate nearest neighbors of $\mathbf{v}_{\text{new}}$
2. **Connect** $\mathbf{v}_{\text{new}}$ to those $M$ neighbors with bidirectional edges

That's it. The graph grows incrementally, and the search procedure itself is used during construction.

The elegant consequence: **early insertions create long-range connections** (because the graph is sparse and search must traverse large distances), while **later insertions create short-range connections** (because the graph is dense and search finds true nearby neighbors). This naturally produces the mix of short-range and long-range edges that gives the small-world property.

### 3.5 Limitations of NSW

NSW works well but has a key weakness: as $N$ grows, the search path length grows too. The greedy search must traverse many short-range edges to navigate from the entry point to the query's neighborhood. The expected search complexity is approximately:

$$
O(N^{1/d} \cdot \log N)
$$

which degrades in high dimensions. HNSW fixes this.

---

## 4. Hierarchical Navigable Small World (HNSW)

HNSW (Malkov and Yashunin, 2018) is the production-grade evolution of NSW. The key idea: **build multiple layers of NSW graphs at different resolutions**, like a hierarchy of increasingly detailed maps.

### 4.1 The Multi-Layer Structure

HNSW maintains $L_{\max}$ layers, numbered from $0$ (bottom, densest) to $L_{\max}$ (top, sparsest):

```text
Layer 3 (sparsest):    o -------- o -------- o
                       |                     |
Layer 2:               o --- o --- o --- o --- o
                       |    |    |    |    |
Layer 1:               o-o-o-o-o-o-o-o-o-o-o-o
                       |||||||||||||||||||||||||
Layer 0 (densest):     ooooooooooooooooooooooooo   <-- all N vectors
```

- **Layer 0** contains **all** $N$ vectors with connections to their nearest neighbors
- **Higher layers** contain **exponentially fewer** vectors, each with longer-range connections
- A vector present at layer $\ell$ is also present at all layers below it ($0, 1, \dots, \ell$)

### 4.2 Layer Assignment

When a new vector is inserted, it is assigned a maximum layer $\ell$ by sampling from a geometric distribution:

$$
\ell = \lfloor -\ln(\text{uniform}(0, 1)) \cdot m_L \rfloor
$$

where $m_L = 1 / \ln(M)$ is a normalization factor and $M$ is the number of connections per node. This gives:

| Layer | Probability of inclusion | Expected number of nodes |
| ----- | ------------------------ | ------------------------ |
| 0 | 1.0 | $N$ |
| 1 | $\sim 1/M$ | $N/M$ |
| 2 | $\sim 1/M^2$ | $N/M^2$ |
| $\ell$ | $\sim 1/M^\ell$ | $N/M^\ell$ |

With $M = 16$ and $N = 10^6$: layer 0 has $10^6$ nodes, layer 1 has approximately 62,500, layer 2 has approximately 3,900, layer 3 has approximately 244, etc. The top layer has $O(1)$ nodes.

### 4.3 HNSW Search Algorithm

Search proceeds **top-down**:

```text
SEARCH_HNSW(q, num_results, ef):
    entry_point = top_layer_entry_node

    # Phase 1: Greedy descent through upper layers (find the right region)
    for layer = L_max down to 1:
        entry_point = greedy_search(q, entry_point, layer, num_neighbors=1)

    # Phase 2: Detailed search at layer 0 (find the actual neighbors)
    results = beam_search(q, entry_point, layer=0, ef=ef)

    return top_k(results, num_results)
```

- **Upper layers** (sparse, long-range edges): coarse navigation to the right region of the space. Each layer narrows the search area. This is like zooming in on a map -- continent, then country, then city, then street.
- **Layer 0** (dense, short-range edges): fine-grained search within the local neighborhood.

The parameter `ef` (exploration factor) controls the beam width at layer 0. Larger `ef` means more exploration, higher recall, but slower search.

### 4.4 HNSW Insertion Algorithm

Inserting a new vector $\mathbf{v}_{\text{new}}$:

```text
INSERT_HNSW(v_new):
    l = random_layer()                    # sample max layer from geometric distribution
    entry_point = top_layer_entry_node

    # Phase 1: Greedy descent to layer l+1 (find entry point for insertion layers)
    for layer = L_max down to l+1:
        entry_point = greedy_search(v_new, entry_point, layer, num_neighbors=1)

    # Phase 2: Insert at each layer from l down to 0
    for layer = l down to 0:
        # Find M closest neighbors at this layer
        neighbors = beam_search(v_new, entry_point, layer, ef=efConstruction)
        candidates = select_neighbors(v_new, neighbors, M)

        # Add bidirectional edges
        for each c in candidates:
            add_edge(v_new, c, layer)
            add_edge(c, v_new, layer)

            # Prune c's connections if it now exceeds M_max
            if degree(c, layer) > M_max:
                prune_connections(c, layer, M_max)

        entry_point = candidates[0]       # use closest neighbor as entry for next layer
```

Key parameters:

| Parameter | Meaning | Typical Value |
| --------- | ------- | ------------- |
| $M$ | Number of connections per node per layer | 16--64 |
| $M_{\max}$ | Maximum connections per node (layer 0 often uses $2M$) | 32--128 |
| $\text{efConstruction}$ | Beam width during insertion (higher = better graph, slower build) | 100--400 |
| $\text{ef}$ | Beam width during search (higher = better recall, slower query) | 50--200 |

### 4.5 Neighbor Selection: Simple vs. Heuristic

When selecting which $M$ neighbors to connect to, HNSW offers two strategies:

**Simple selection**: Pick the $M$ closest candidates. Fast but can create redundant edges in clustered regions -- all edges point into the same dense cluster, leaving other directions unreachable.

**Heuristic selection** (Algorithm 4 in the paper): Prefer neighbors that are **diverse** -- i.e., not too close to each other. The heuristic iterates through candidates sorted by distance and only keeps a candidate if it is closer to $\mathbf{v}_{\text{new}}$ than to any already-selected neighbor:

$$
\text{Keep } c_j \quad \text{if} \quad d(\mathbf{v}_{\text{new}},\; c_j) < \min_{s \in S} \; d(s,\; c_j)
$$

where $S$ is the set of already-selected neighbors. This ensures **angular diversity** -- the selected neighbors cover different directions around $\mathbf{v}_{\text{new}}$, which dramatically improves navigability.

**Example**: Suppose $\mathbf{v}_{\text{new}}$ sits between two clusters A and B. Simple selection might pick 16 neighbors all from cluster A (the closer one). Heuristic selection would pick some from A and some from B, ensuring the graph can navigate between clusters.

---

## 5. Why HNSW Search Is Logarithmic

### 5.1 Intuition

At the top layer, the graph has $O(1)$ nodes -- we can find the closest one in constant time. Each subsequent layer has $M$ times more nodes, so we need $O(\log_M N)$ layers to reach layer 0. At each layer, the greedy search takes $O(\log(N / M^\ell))$ steps. The total search cost is:

$$
T_{\text{search}} = \sum_{\ell=0}^{L_{\max}} O\!\left(\log \frac{N}{M^\ell}\right) = O(\log^2 N)
$$

In practice, with the beam search at layer 0 dominating, the effective complexity is:

$$
O(\log N \cdot d)
$$

where $d$ is the vector dimension (cost of each distance computation).

### 5.2 Comparison with Other ANN Methods

| Method | Build Time | Query Time | Memory | Recall |
| ------ | ---------- | ---------- | ------ | ------ |
| Brute-force | $O(Nd)$ | $O(Nd)$ | $O(Nd)$ | 100% |
| LSH | $O(Nd)$ | $O(d \cdot N^{1/c})$ | $O(Nd)$ | Tunable |
| IVF (Inverted File) | $O(Nd + k_{\text{means}})$ | $O(n_{\text{probe}} \cdot N/k)$ | $O(Nd)$ | Tunable |
| **HNSW** | $O(N \log N \cdot d)$ | $O(\log N \cdot d)$ | $O(NMd)$ | Tunable |
| Product Quantization | $O(Nd)$ | $O(Nd')$ ($d' \ll d$) | $O(N \cdot d/m)$ | Lower |

HNSW's main tradeoff: it uses **more memory** (storing the graph edges) in exchange for **faster queries** and **higher recall**. The graph overhead is $O(NM)$ pointers, which is typically small compared to the vectors themselves.

---

## 6. Practical Considerations

### 6.1 When to Use HNSW

HNSW is the right choice when:

- $N \geq 100{,}000$ vectors (below this, brute-force may be simpler and fast enough)
- **Low latency** is critical (sub-millisecond queries)
- **High recall** is required ($> 95\%$)
- The dataset fits in memory (HNSW is an in-memory index)

### 6.2 When HNSW Struggles

- **Very high intrinsic dimensionality**: If the data truly lives in a high-dimensional manifold (not just high ambient dimension), all points become roughly equidistant and graph navigation loses its advantage. This is a manifestation of the **curse of dimensionality**.
- **Extremely large datasets** ($N > 10^9$): The memory overhead of storing the graph becomes significant. Disk-based or quantized variants (DiskANN, SPANN) are preferred.
- **Frequently updated datasets**: Insertions are efficient ($O(\log N)$ each), but deletions require graph repair, which is more complex.

### 6.3 Tuning Guidelines

| Goal | Adjust |
| ---- | ------ |
| Higher recall | Increase `ef` (search beam width) |
| Faster queries | Decrease `ef` |
| Better graph quality | Increase `efConstruction` and `M` |
| Lower memory | Decrease `M` |
| Faster index build | Decrease `efConstruction` |

The typical workflow: build with high `efConstruction` (one-time cost), then tune `ef` at query time to hit the desired recall-latency tradeoff.

---

## 7. HNSW in the RAG Pipeline

In a Retrieval-Augmented Generation (RAG) system, HNSW sits at the retrieval stage:

```text
User query
  --> Embedding model (e.g., BAAI/bge-base-en-v1.5) --> query vector q
    --> HNSW index search --> top-k document vectors
      --> Retrieve original text chunks
        --> Feed to LLM as context
          --> Generate answer
```

The embedding model (a Sentence Transformer -- see the [Sentence Transformer tutorials](../sentence_transformer/)) produces the vectors. HNSW provides the fast lookup. The quality of the final answer depends on both:

- **Embedding quality**: Do similar documents have similar vectors? (Determined by the Sentence Transformer's training data and loss function)
- **Search quality**: Does the index return the actual nearest neighbors? (Determined by HNSW's graph structure and search parameters)

---

## 8. Summary

| Concept | NSW | HNSW |
| ------- | --- | ---- |
| Structure | Single-layer proximity graph | Multi-layer hierarchy of proximity graphs |
| Construction | Incremental insertion with graph search | Incremental insertion with layer assignment |
| Search | Beam search from random entry | Top-down greedy descent + beam search at layer 0 |
| Complexity (search) | $O(N^{1/d} \log N)$ | $O(\log N)$ |
| Complexity (build) | $O(N \log N)$ | $O(N \log N)$ |
| Key insight | Early insertions create long-range links | Hierarchy separates coarse and fine navigation |

The fundamental insight behind both: **the graph itself is the index**. By encoding proximity relationships as edges, we transform nearest neighbor search from a geometric problem (scanning a space) into a graph traversal problem (navigating a network). The small-world structure ensures this traversal is efficient.

---

## References

- Malkov, Y. A., and Yashunin, D. A. (2018). *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs*. IEEE TPAMI.
- Malkov, Y. A., et al. (2014). *Approximate Nearest Neighbor Algorithm Based on Navigable Small World Graphs*. Information Systems.
- Watts, D. J., and Strogatz, S. H. (1998). *Collective Dynamics of 'Small-World' Networks*. Nature.
- Johnson, J., Douze, M., and Jegou, H. (2019). *Billion-Scale Similarity Search with GPUs (FAISS)*. IEEE TBD.
- Bernhardsson, E. (2018). *ANN Benchmarks*. [ann-benchmarks.com](https://ann-benchmarks.com/)

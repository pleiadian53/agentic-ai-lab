# Clustering in High-Dimensional Spaces

> **Series**: Multi-Vector Image Retrieval
> **Part**: 02 — Clustering Foundations
> **Prerequisite**: [01 — Prerequisites for Multi-Vector Retrieval](./01_multivector_text_retrieval.md)

Clustering is a natural companion to embedding-based retrieval. Once objects live in a vector space, grouping them by proximity reveals structure — topics in a document corpus, cell types in single-cell data, visual concepts in image patches. But the same high-dimensional geometry that makes retrieval hard also undermines classical clustering algorithms.

This document covers why standard k-means fails in high dimensions, what alternatives exist, and whether dimensionality reduction helps as a preprocessing step.

---

## 1. Why K-Means Struggles in High Dimensions

Standard k-means minimizes the within-cluster sum of squared Euclidean distances:

$$
\arg\min_{\{C_k\}} \sum_{k=1}^{K} \sum_{\mathbf{x} \in C_k} \|\mathbf{x} - \boldsymbol{\mu}_k\|_2^2
$$

where $\boldsymbol{\mu}_k$ is the centroid of cluster $C_k$. This works well in low dimensions but degrades as $d$ grows, for three interconnected reasons.

### 1.1 Distance Concentration

In high-dimensional spaces, pairwise Euclidean distances concentrate around a common value. For random vectors in $\mathbb{R}^d$, the ratio of the maximum to minimum pairwise distance converges to 1 as $d \to \infty$:

$$
\frac{\max_{i,j} \|\mathbf{x}_i - \mathbf{x}_j\|}{\min_{i,j} \|\mathbf{x}_i - \mathbf{x}_j\|} \xrightarrow{d \to \infty} 1
$$

When all distances look the same, the assignment step of k-means — "assign each point to the nearest centroid" — becomes nearly arbitrary. Small perturbations in the data or initialization can flip assignments, leading to unstable, meaningless clusters.

### 1.2 The Curse of Sparsity

As dimensionality increases, data points become increasingly sparse relative to the volume of the space. The number of samples needed to maintain a given density grows exponentially with $d$. In practice, this means that even large datasets are effectively sparse in high dimensions, and local neighborhoods contain too few points for meaningful centroid estimation.

### 1.3 Irrelevant Dimensions

In high-dimensional data, many dimensions may carry noise rather than signal. K-means treats all dimensions equally, so noisy dimensions dilute the meaningful distance signal. A pair of points that are close in the 10 informative dimensions may appear far apart when measured across all 1000 dimensions.

---

## 2. Cosine K-Means: Spherical K-Means

The most direct fix for k-means in embedding spaces is to replace Euclidean distance with cosine similarity. This variant is known as **Spherical K-Means**.

### Algorithm

1. **Normalize** all data points to unit length: $\hat{\mathbf{x}}_i = \mathbf{x}_i / \|\mathbf{x}_i\|$
2. **Assign** each point to the cluster whose centroid has the highest cosine similarity:

$$
c_i = \arg\max_{k} \; \frac{\hat{\mathbf{x}}_i \cdot \boldsymbol{\mu}_k}{\|\boldsymbol{\mu}_k\|}
$$

3. **Update** centroids as the mean of assigned points, then re-normalize:

$$
\boldsymbol{\mu}_k = \frac{\sum_{\mathbf{x} \in C_k} \hat{\mathbf{x}}}{\left\|\sum_{\mathbf{x} \in C_k} \hat{\mathbf{x}}\right\|}
$$

4. Repeat until convergence.

### Why It Helps

- Cosine similarity measures **angle**, which remains discriminative in high dimensions (unlike Euclidean distance)
- Naturally suited to embedding vectors, which are often $\ell_2$-normalized by the embedding model
- Equivalent to k-means on the unit hypersphere $\mathcal{S}^{d-1}$

### Implementation

Spherical k-means is not in scikit-learn's standard `KMeans`, but it is straightforward to implement:

```python
import numpy as np
from sklearn.preprocessing import normalize

def spherical_kmeans(X, n_clusters, max_iter=100, tol=1e-4):
    """Spherical k-means clustering using cosine similarity."""
    X_norm = normalize(X, norm='l2')  # Project onto unit sphere
    
    # Initialize centroids (k-means++ style on normalized data)
    rng = np.random.default_rng(42)
    indices = rng.choice(len(X_norm), n_clusters, replace=False)
    centroids = X_norm[indices].copy()
    
    for iteration in range(max_iter):
        # Assign: cosine similarity = dot product for unit vectors
        similarities = X_norm @ centroids.T
        labels = similarities.argmax(axis=1)
        
        # Update centroids
        new_centroids = np.zeros_like(centroids)
        for k in range(n_clusters):
            members = X_norm[labels == k]
            if len(members) > 0:
                new_centroids[k] = members.mean(axis=0)
        new_centroids = normalize(new_centroids, norm='l2')
        
        # Check convergence
        shift = np.linalg.norm(new_centroids - centroids)
        centroids = new_centroids
        if shift < tol:
            break
    
    return labels, centroids
```

Alternatively, normalize the data and use standard `KMeans` — on unit-norm vectors, minimizing squared Euclidean distance is equivalent to maximizing cosine similarity:

$$
\|\hat{\mathbf{x}} - \hat{\mathbf{y}}\|_2^2 = 2 - 2 \cos(\hat{\mathbf{x}}, \hat{\mathbf{y}})
$$

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

X_norm = normalize(X, norm='l2')
kmeans = KMeans(n_clusters=8, random_state=42)
labels = kmeans.fit_predict(X_norm)
```

This is the simplest practical approach and works well for moderate dimensions ($d \leq 1000$).

---

## 3. Other K-Means Variants for High Dimensions

### 3.1 Mini-Batch K-Means

Not a distance fix, but a scalability fix. Uses random subsets (mini-batches) per iteration instead of the full dataset. Critical when $N$ is large (millions of embeddings):

```python
from sklearn.cluster import MiniBatchKMeans

mbk = MiniBatchKMeans(n_clusters=100, batch_size=1024, random_state=42)
labels = mbk.fit_predict(X_norm)
```

Combine with $\ell_2$-normalization for cosine-based mini-batch k-means.

### 3.2 K-Means with Mahalanobis Distance

Replaces Euclidean distance with the Mahalanobis distance, which accounts for feature correlations:

$$
d_M(\mathbf{x}, \boldsymbol{\mu}) = \sqrt{(\mathbf{x} - \boldsymbol{\mu})^T \Sigma^{-1} (\mathbf{x} - \boldsymbol{\mu})}
$$

This is equivalent to k-means after whitening the data. In practice, estimating $\Sigma^{-1}$ in high dimensions requires regularization or dimensionality reduction first.

### 3.3 Kernel K-Means

Maps data into a higher-dimensional feature space via a kernel function, then runs k-means in that space. Useful when clusters are non-convex in the original space. Computationally expensive ($O(N^2)$ kernel matrix), so typically used with approximations or on smaller datasets.

---

## 4. Beyond K-Means: Algorithms for High-Dimensional Clustering

When k-means variants are insufficient, several algorithm families handle high-dimensional data more gracefully.

### 4.1 Gaussian Mixture Models (GMM)

GMMs model each cluster as a multivariate Gaussian and fit via Expectation-Maximization:

$$
p(\mathbf{x}) = \sum_{k=1}^{K} \pi_k \, \mathcal{N}(\mathbf{x} \mid \boldsymbol{\mu}_k, \Sigma_k)
$$

**Advantages over k-means**:

- Soft assignments (probabilistic cluster membership)
- Each cluster can have its own covariance structure (ellipsoidal, not just spherical)
- Model selection via BIC/AIC

**High-dimensional challenge**: Full covariance matrices have $O(d^2)$ parameters per cluster. Solutions:

- **Diagonal covariance** — assumes feature independence (fast but restrictive)
- **Tied covariance** — all clusters share one covariance matrix
- **Factor-analyzed covariance** — low-rank approximation: $\Sigma_k = W_k W_k^T + \sigma^2 I$

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(
    n_components=8,
    covariance_type='diag',  # or 'full', 'tied', 'spherical'
    random_state=42,
)
labels = gmm.fit_predict(X)
```

### 4.2 HDBSCAN: Density-Based Clustering

**HDBSCAN** (Hierarchical DBSCAN) is the go-to density-based method. It finds clusters of varying density without requiring a pre-specified number of clusters.

**Why it works in high dimensions**:

- Does not assume convex or spherical clusters
- Automatically identifies noise points (outliers)
- Hierarchical approach adapts to local density variations
- The `min_cluster_size` parameter is more intuitive than $k$

**Caveat**: In very high dimensions ($d > 100$), density estimation becomes unreliable due to the curse of dimensionality. Dimensionality reduction before HDBSCAN is strongly recommended.

```python
import hdbscan

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=15,
    min_samples=5,
    metric='euclidean',  # or 'cosine' via precomputed distances
)
labels = clusterer.fit_predict(X_reduced)  # After dimensionality reduction
```

For cosine distance:

```python
from sklearn.metrics.pairwise import cosine_distances

dist_matrix = cosine_distances(X)
clusterer = hdbscan.HDBSCAN(min_cluster_size=15, metric='precomputed')
labels = clusterer.fit_predict(dist_matrix)
```

### 4.3 Spectral Clustering

Constructs a similarity graph from the data, then clusters the eigenvectors of the graph Laplacian. Effective for non-convex cluster shapes.

**High-dimensional considerations**:

- Building the full similarity matrix is $O(N^2 d)$ — expensive for large $N$
- The eigendecomposition is $O(N^3)$ for the full Laplacian
- Approximate methods (Nyström, random features) make it feasible for moderate $N$

```python
from sklearn.cluster import SpectralClustering

sc = SpectralClustering(
    n_clusters=8,
    affinity='nearest_neighbors',  # Sparse graph, scalable
    n_neighbors=10,
    random_state=42,
)
labels = sc.fit_predict(X)
```

### 4.4 Subspace Clustering

When clusters exist in different low-dimensional subspaces of the ambient space, subspace clustering methods outperform standard approaches.

**Key algorithms**:

- **Sparse Subspace Clustering (SSC)** — represents each point as a sparse combination of others; the sparsity pattern reveals cluster structure
- **Low-Rank Representation (LRR)** — similar idea but enforces low-rank structure
- **CLIQUE / SUBCLU** — grid-based subspace clustering for axis-aligned subspaces

These are particularly relevant for genomic data, where different gene modules may define clusters in different subsets of features.

### 4.5 Locality-Sensitive Hashing (LSH) Based Clustering

For extremely high dimensions ($d > 10{,}000$) and very large $N$, LSH can be used to build approximate nearest-neighbor graphs, which then feed into graph-based clustering:

1. Use LSH to find approximate neighbors for each point
2. Build a k-NN graph from the LSH results
3. Apply community detection (Louvain, Leiden) on the graph

This is the approach used by **Scanpy's Leiden clustering** for single-cell RNA-seq data (typically $d = 2{,}000$–$30{,}000$ genes).

---

## 5. Dimensionality Reduction as Preprocessing: Does It Help?

**Short answer: yes, almost always, but the choice of method matters.**

The intuition is straightforward: if the intrinsic dimensionality of the data is $d^* \ll d$, then clustering in the original $d$-dimensional space wastes capacity on noise. Reducing to a space closer to $d^*$ concentrates the signal and makes distances more meaningful.

### 5.1 PCA (Principal Component Analysis)

**Linear** projection onto the top $k$ principal components.

$$
\mathbf{z} = W^T \mathbf{x}, \quad W \in \mathbb{R}^{d \times k}
$$

**When to use**: Always a reasonable first step. Fast, deterministic, and preserves global variance structure. Works well when the data lies near a linear subspace.

**Limitations**: Cannot capture nonlinear manifold structure. If clusters are separated by curved boundaries, PCA may mix them.

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=50)
X_pca = pca.fit_transform(X)
# Then cluster X_pca
```

**Rule of thumb**: Reduce to the number of components that capture 90–95% of variance, or use the elbow in the explained variance plot.

### 5.2 UMAP (Uniform Manifold Approximation and Projection)

**Nonlinear** dimensionality reduction that preserves both local and global structure.

**When to use**: When the data has nonlinear manifold structure (common for embeddings). UMAP is the standard preprocessing step before HDBSCAN in many domains (single-cell genomics, NLP embedding analysis, image feature clustering).

```python
import umap

reducer = umap.UMAP(n_components=15, n_neighbors=15, min_dist=0.1, metric='cosine')
X_umap = reducer.fit_transform(X)
# Then cluster X_umap
```

**Critical detail**: For clustering, use a **higher target dimension** (e.g., 15–50) than for visualization (2–3). The 2D UMAP plot is for human inspection; the 15D UMAP embedding is for clustering.

**Limitations**:

- Non-deterministic (depends on random initialization)
- `n_neighbors` and `min_dist` significantly affect results — requires tuning
- Can create artificial clusters in the 2D projection that don't exist in the original space

### 5.3 t-SNE

**Nonlinear** reduction optimized for visualization (2D/3D).

**For clustering: generally not recommended.** t-SNE distorts distances and densities in ways that make downstream clustering unreliable. Clusters that appear separated in a t-SNE plot may overlap in the original space, and vice versa.

Use t-SNE for visualization *after* clustering, not as a preprocessing step *before* clustering.

### 5.4 Random Projection

**Linear** projection using a random matrix, justified by the Johnson-Lindenstrauss lemma:

> For any $\epsilon > 0$ and $N$ points in $\mathbb{R}^d$, a random projection into $\mathbb{R}^k$ with $k = O(\epsilon^{-2} \log N)$ preserves all pairwise distances within a factor of $(1 \pm \epsilon)$.

This is remarkably powerful: you can reduce 10,000 dimensions to a few hundred while approximately preserving all distances, with no data-dependent fitting.

```python
from sklearn.random_projection import GaussianRandomProjection

rp = GaussianRandomProjection(n_components=256, random_state=42)
X_rp = rp.fit_transform(X)
```

**When to use**: As a fast, parameter-free preprocessing step when $d$ is very large and you need a quick reduction before applying k-means or HDBSCAN. Less effective than PCA or UMAP at concentrating signal, but much faster and with theoretical guarantees.

### 5.5 Autoencoders (Deep Dimensionality Reduction)

For very complex data (images, long sequences), a learned nonlinear encoder can produce embeddings that are more clusterable than PCA or UMAP outputs:

$$
\mathbf{z} = f_\theta(\mathbf{x}), \quad f_\theta : \mathbb{R}^d \to \mathbb{R}^k
$$

Variants like **Variational Autoencoders (VAE)** and **Deep Embedded Clustering (DEC)** jointly learn the embedding and cluster assignments.

**When to use**: When you have enough data to train a neural network and the raw features are very high-dimensional (pixels, raw sequences). For pre-computed embeddings (e.g., from BERT or CLIP), the embedding model has already done this step.

---

## 6. Recommended Pipelines by Dimensionality

### Moderate Dimensions ($d \leq 100$)

Most clustering algorithms work reasonably well. Standard approaches:

| Method | Notes |
| ------ | ----- |
| K-means (with $\ell_2$-normalization) | Fast, simple, good baseline |
| GMM (full covariance) | Soft assignments, ellipsoidal clusters |
| HDBSCAN | No need to specify $k$, handles noise |

### High Dimensions ($100 < d \leq 1{,}000$)

Distance concentration starts to bite. Preprocessing helps:

| Pipeline | Notes |
| -------- | ----- |
| $\ell_2$-normalize → K-means | Cosine k-means, strong baseline for embeddings |
| PCA (50–100 dims) → HDBSCAN | Removes noise dimensions, then density-based clustering |
| UMAP (15–50 dims) → HDBSCAN | Captures nonlinear structure, standard in single-cell |

### Very High Dimensions ($d > 1{,}000$)

Dimensionality reduction is essentially mandatory:

| Pipeline | Notes |
| -------- | ----- |
| PCA (50–200) → $\ell_2$-normalize → K-means | Fast, scalable, good for large $N$ |
| PCA (50) → UMAP (15) → Leiden/HDBSCAN | The Scanpy pipeline, proven on $d = 30{,}000$ |
| Random Projection (256) → K-means | When speed matters more than precision |

### Extremely High Dimensions ($d > 10{,}000$) with Large $N$

Graph-based approaches dominate:

| Pipeline | Notes |
| -------- | ----- |
| PCA (50) → k-NN graph → Leiden | Scanpy's default for scRNA-seq |
| LSH → approximate k-NN graph → Louvain | Scales to millions of points |
| Random Projection → Mini-Batch K-means | Fastest option, sacrifices quality |

---

## 7. The Dimensionality Reduction + Clustering Interaction

A subtle but important point: dimensionality reduction and clustering are not independent steps. The reduction method imposes assumptions about what structure to preserve, which directly affects what clusters emerge.

### What Each Method Preserves

| Method | Preserves | Distorts |
| ------ | --------- | -------- |
| **PCA** | Global variance, linear separability | Nonlinear manifold structure |
| **UMAP** | Local neighborhoods, manifold topology | Global distances, densities |
| **t-SNE** | Local neighborhoods (very local) | Everything else |
| **Random Projection** | Pairwise distances (approximately) | Nothing specific (random) |
| **Autoencoders** | Whatever the loss function encodes | Depends on architecture |

### Practical Guidance

- **Always try $\ell_2$-normalization + standard k-means first** as a baseline. It is surprisingly effective for embedding vectors.
- **PCA is almost always beneficial** as a first reduction step, even before UMAP. It removes noise dimensions cheaply and makes subsequent nonlinear methods faster and more stable.
- **UMAP before HDBSCAN** is the most popular pipeline for exploratory clustering of embeddings, but tune `n_components` for clustering (15–50), not visualization (2).
- **Validate clusters** using metrics that don't depend on the reduction: silhouette score in the original space, or downstream task performance.
- **Beware of t-SNE for clustering** — it is a visualization tool, not a preprocessing tool. Clusters in t-SNE plots can be artifacts.

---

## 8. Connection to Multi-Vector Retrieval

These clustering concepts connect directly to the retrieval pipeline:

**MUVERA** (Multi-Vector Retrieval via Aggregation), introduced in the L1 helper utilities (`notebooks/image_retrieval/colbert/helper.py`), uses **SimHash clustering** to group token embeddings into fixed clusters before aggregation. This is a form of high-dimensional clustering applied to 128-dimensional ColBERT token vectors, where:

- SimHash acts as an extremely fast locality-sensitive hash (binary projection)
- Tokens are assigned to $2^k$ clusters based on the sign pattern of random projections
- Document tokens are aggregated per cluster via averaging
- Query tokens are aggregated per cluster via summing

This is essentially a random-projection-based clustering scheme optimized for speed over quality — appropriate because the downstream MaxSim scoring is tolerant of approximate cluster assignments.

**Product Quantization** in vector databases (FAISS, Qdrant) is another form of high-dimensional clustering: the vector space is split into subspaces, and k-means is run independently in each subspace to create a codebook. This reduces storage while preserving approximate distances — a direct application of subspace clustering ideas.

---

## References

- Aggarwal, C.C., Hinneburg, A., & Keim, D.A. (2001). "On the Surprising Behavior of Distance Metrics in High Dimensional Space." *ICDT*.
- Arthur, D. & Vassilvitskii, S. (2007). "k-means++: The Advantages of Careful Seeding." *SODA*.
- Dhillon, I.S. & Modha, D.S. (2001). "Concept Decompositions for Large Sparse Text Data Using Clustering." *Machine Learning*.
- McInnes, L., Healy, J., & Astels, S. (2017). "hdbscan: Hierarchical density based clustering." *JOSS*.
- McInnes, L., Healy, J., & Melville, J. (2018). "UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction." *arXiv:1802.03426*.
- Johnson, W.B. & Lindenstrauss, J. (1984). "Extensions of Lipschitz mappings into a Hilbert space." *Contemporary Mathematics*.
- Traag, V.A., Waltman, L., & van Eck, N.J. (2019). "From Louvain to Leiden: guaranteeing well-connected communities." *Scientific Reports*.
- Wolf, F.A., Angerer, P., & Theis, F.J. (2018). "SCANPY: large-scale single-cell gene expression data analysis." *Genome Biology*.

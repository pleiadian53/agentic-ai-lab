# Vectorized Batch Cosine Similarity

**Source**: `cosine_similarity()` in `C1M2_Ungraded_Lab_2.ipynb`, 2D branch  
**Context**: Used in `compute_metrics()` to score all 11,314 document embeddings against
a query embedding in a single pass.

---

## 1. The Formula

Cosine similarity between two vectors $\mathbf{u}$ and $\mathbf{v}$ is:

$$
\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \, \|\mathbf{v}\|}
$$

It measures the **angle** between vectors, not their magnitude. A value of 1 means identical
direction (maximum similarity); 0 means orthogonal (no similarity); −1 means opposite direction.

For a query vector $\mathbf{q} \in \mathbb{R}^d$ against a corpus of $N$ document vectors,
the naive approach is a loop:

```python
scores = [cosine_similarity(q, doc) for doc in corpus]   # N iterations
```

The 2D branch replaces this loop with a single matrix operation.

---

## 2. The Full Function (Context)

```python
def cosine_similarity(v1, array_of_vectors):
    # Normalize inputs to NumPy float32
    v1 = np.asarray(v1, dtype=np.float32).ravel()          # shape: (D,)
    A  = np.asarray(array_of_vectors, dtype=np.float32)    # shape: (D,) or (N, D)

    if A.ndim == 1:
        # Single vector: classic dot-product formula
        denom = np.linalg.norm(v1) * np.linalg.norm(A)
        return float(0.0 if denom == 0 else np.dot(v1, A) / denom)

    # Vectorized batch case — explained below
    A = np.atleast_2d(A)
    v1_norm = np.linalg.norm(v1)
    A_norms = np.linalg.norm(A, axis=1)
    denom = v1_norm * A_norms
    with np.errstate(divide='ignore', invalid='ignore'):
        sims = (A @ v1) / np.where(denom == 0, 1.0, denom)
    sims[denom == 0] = 0.0
    return sims.tolist()
```

---

## 3. Line-by-Line Walkthrough of the 2D Branch

### Line 1 — Guarantee a 2D matrix

```python
A = np.atleast_2d(A)
```

`A` is already `(N, D)` after `np.asarray`, but `np.atleast_2d` is a defensive guard: if a
single embedding of shape `(D,)` somehow reaches this branch, it is promoted to `(1, D)`.
Without this, the `axis=1` norm call on the next line would fail.

**Shape after**: `A` is `(N, D)` — $N$ document vectors, each of dimension $D$.

---

### Line 2 — L2 norm of the query vector

```python
v1_norm = np.linalg.norm(v1)
```

Computes $\|\mathbf{v_1}\|_2 = \sqrt{\sum_{i=1}^{D} v_{1,i}^2}$ — a single scalar.

This is computed **once** and reused for all $N$ comparisons. In the loop version it would
be recomputed $N$ times.

**Shape**: scalar `float32`.

---

### Line 3 — L2 norm of every document vector

```python
A_norms = np.linalg.norm(A, axis=1)
```

`axis=1` tells NumPy to reduce along the column dimension — i.e., compute the L2 norm of
each **row** independently:

$$
\text{A\_norms}[i] = \|\mathbf{a}_i\|_2 = \sqrt{\sum_{j=1}^{D} A_{ij}^2}, \quad i = 0, \ldots, N-1
$$

**Shape**: `(N,)` — one norm value per document.

---

### Line 4 — Denominator for all N similarities

```python
denom = v1_norm * A_norms
```

Broadcasting: a scalar times a vector of length $N$ produces a vector of length $N$:

$$
\text{denom}[i] = \|\mathbf{v_1}\| \cdot \|\mathbf{a}_i\|
$$

This is the denominator of the cosine formula for each document.

**Shape**: `(N,)`.

---

### Lines 5–7 — Numerator and safe division

```python
with np.errstate(divide='ignore', invalid='ignore'):
    sims = (A @ v1) / np.where(denom == 0, 1.0, denom)
```

**`A @ v1`** — matrix-vector product:

$$
(\mathbf{A}\mathbf{v_1})[i] = \sum_{j=1}^{D} A_{ij} \cdot v_{1,j} = \mathbf{a}_i \cdot \mathbf{v_1}
$$

This is the **dot product of $\mathbf{v_1}$ with every row of $A$** simultaneously —
the numerator of the cosine formula for all $N$ documents in one operation.

**Shape**: `(N,)`.

**`np.where(denom == 0, 1.0, denom)`** — safe denominator: replaces any zero-norm entry
with `1.0` to avoid division by zero. The final division then gives a *non-NaN* value for
those entries (which gets corrected to `0.0` in the next line).

**`np.errstate(divide='ignore', invalid='ignore')`** — suppresses the floating-point
warnings that NumPy would otherwise emit for `0/0` or `x/0` operations, keeping the output
clean even before the explicit correction on the next line.

**Shape of `sims`**: `(N,)` — one similarity score per document.

---

### Line 8 — Zero-norm correction

```python
sims[denom == 0] = 0.0
```

A document with a zero-norm embedding vector (all zeros) has no meaningful direction, so
its cosine similarity is defined as 0 by convention. This line overwrites the placeholder
values inserted by `np.where` in the previous step.

---

## 4. Why Vectorization Matters

For the 20 Newsgroups corpus ($N = 11{,}314$ documents, $D = 768$ dimensions):

| Approach | Operations | Dominant cost |
|---|---|---|
| Loop | $N$ dot products, 1 at a time | Python interpreter overhead × 11,314 |
| Vectorized (`A @ v1`) | 1 matrix-vector multiply $(N \times D)$ | Single BLAS call (highly optimized) |

The vectorized version is typically **50–200× faster** in practice because BLAS (Basic Linear
Algebra Subprograms) routines, which NumPy uses internally, execute the matrix multiply with
highly optimized CPU instructions (SIMD, cache-blocking).

---

## 5. Complete Data Flow

```
Input:
  v1  : shape (D,)      — query embedding, e.g. D=768 for bge-base-en-v1.5
  A   : shape (N, D)    — stacked corpus embeddings, N=11314

Step 1  np.atleast_2d(A)      → A        : (N, D)
Step 2  np.linalg.norm(v1)    → v1_norm  : scalar
Step 3  np.linalg.norm(A,1)   → A_norms  : (N,)
Step 4  v1_norm * A_norms     → denom    : (N,)
Step 5  A @ v1                → dots     : (N,)   ← N dot products in one BLAS call
Step 6  dots / denom          → sims     : (N,)   ← element-wise division
Step 7  sims[denom==0] = 0.0  → sims     : (N,)   ← zero-norm guard

Output:
  sims.tolist()  → list of N floats ∈ [−1, 1]
```

---

## 6. Numerical Example (Toy, D=3)

```python
v1 = [1, 0, 0]         # query: points along x-axis
A  = [[1, 0, 0],       # doc 0: identical to query  → sim = 1.0
      [0, 1, 0],       # doc 1: orthogonal          → sim = 0.0
      [1, 1, 0],       # doc 2: 45° angle           → sim = 0.707
      [0, 0, 0]]       # doc 3: zero vector         → sim = 0.0 (by convention)

v1_norm = 1.0
A_norms = [1.0, 1.0, 1.414, 0.0]
denom   = [1.0, 1.0, 1.414, 0.0]   # zero for doc 3 → replaced by 1.0 in np.where
A @ v1  = [1.0, 0.0, 1.0,   0.0]   # dot products
sims    = [1.0, 0.0, 0.707, 0.0]   # after zero-norm correction
```

---

*Document created: 2026-02-20 · Context: `C1M2_Ungraded_Lab_2.ipynb` (Retrieval Metrics)*

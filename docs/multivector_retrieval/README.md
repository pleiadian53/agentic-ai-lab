# Multi-Vector Image Retrieval

This series covers the theory and practice of multi-vector retrieval — from foundational concepts (embeddings, similarity, ANN search) through hands-on implementation with ColBERT, Qdrant, and ColPali.

---

## Tutorial Documents

| # | Document | Topics |
| - | -------- | ------ |
| 01 | [Prerequisites for Multi-Vector Retrieval](./01_multivector_text_retrieval.md) | Dense embeddings, similarity functions, ANN search, HNSW, MaxSim |
| 02 | [Clustering in High-Dimensional Spaces](./02_clustering_in_high_dimensions.md) | Spherical k-means, HDBSCAN, spectral clustering, PCA/UMAP preprocessing |

---

## Related Notebooks

The hands-on notebooks live under [`notebooks/image_retrieval/`](../../notebooks/image_retrieval/):

| Notebook | Description |
| -------- | ----------- |
| [L1 — ColBERT Multi-Vector Text Retrieval](../../notebooks/image_retrieval/colbert/L1.ipynb) | ColBERT embeddings, MaxSim scoring, dense vs. multi-vector comparison using Qdrant |

---

## Library Reference

Detailed tutorials for the key libraries used in the notebooks:

| Tutorial | Covers |
| -------- | ------ |
| [Fastembed Tutorial](../../notebooks/image_retrieval/colbert/docs/fastembed_tutorial.md) | Dense & ColBERT embedding models, asymmetric encoding, batch processing |
| [Qdrant Tutorial](../../notebooks/image_retrieval/colbert/docs/qdrant_tutorial.md) | Vector database setup, multi-vector collections, hybrid retrieval, quantization |

---

## Environment Setup

See the [Image Retrieval README](../../notebooks/image_retrieval/README.md#environment-setup) for instructions on setting up the dedicated `image-retrieval` conda environment (macOS and RunPod/CUDA).

# Semantic Search Beyond Text: Images, Molecules, and 3D Structures

**Extending the encoder + pooling + contrastive loss paradigm to visual, chemical, and geometric domains.**

Related reading:

- [How Sentence Transformers Work](../sentence_transformer/01_how_sentence_transformers_work.md)
- [Biological Sequence Embeddings](../sentence_transformer/03_biological_sequence_embeddings.md)

---

## 1. The Recurring Pattern

In Part 1 of the Sentence Transformer series, we established a design pattern:

```text
Tokenizer / Encoder → Pooling → Fixed-size embedding → Contrastive loss
```

This pattern has now been applied to virtually every data modality. The question is always the same: **how do you define the encoder, the pooling, and the positive pairs?**

This document covers three domains where semantic search is increasingly important and technically challenging:

1. **Images** — including medical imaging and pathology
2. **Molecular structures** — small molecules, drugs, and chemical similarity
3. **3D objects and surfaces** — point clouds, meshes, and protein structures

Each domain has its own "Sentence Transformer moment" — a point where contrastive metric learning produced embeddings good enough for practical retrieval.

---

## 2. Image Embeddings and Visual Semantic Search

### 2.1 The Image Encoder Landscape

Images do not have a sequential token structure like text. Instead, image encoders use one of two strategies:

- **Convolutional Neural Networks (CNNs)**: Learn hierarchical spatial features through convolution and pooling. ResNet, EfficientNet, and ConvNeXt are representative architectures.
- **Vision Transformers (ViT)**: Split the image into fixed-size patches (e.g., 16x16 pixels), treat each patch as a "token," and process them with a standard Transformer encoder.

The ViT approach is the direct visual analogue of a Sentence Transformer:

| Component | Sentence Transformer | Vision Transformer |
| --------- | -------------------- | ------------------ |
| Input | Word/subword tokens | Image patches (e.g., 16x16) |
| Encoder | BERT-like Transformer | ViT Transformer |
| Pooling | Mean over tokens | CLS token or mean over patches |
| Output | Sentence embedding in $\mathbb{R}^d$ | Image embedding in $\mathbb{R}^d$ |

### 2.2 CLIP: The Breakthrough for Visual Semantic Search

**CLIP** (Contrastive Language-Image Pre-training; Radford et al., 2021) is the model that made image semantic search practical at scale. It is, conceptually, a **Sentence Transformer and an Image Transformer trained jointly**.

Architecture:

- A **text encoder** (Transformer) maps captions to $\mathbb{R}^d$.
- An **image encoder** (ViT or ResNet) maps images to $\mathbb{R}^d$.
- Both encoders are trained with **InfoNCE loss** on (image, caption) pairs.

The training objective is identical to Part 2's InfoNCE implementation, except the anchor and positive come from different modalities:

$$
\mathcal{L}_i = -\log \frac{\exp\!\big(\text{sim}(\mathbf{v}_i, \mathbf{t}_i) / \tau\big)}{\displaystyle\sum_{j=1}^{N} \exp\!\big(\text{sim}(\mathbf{v}_i, \mathbf{t}_j) / \tau\big)}
$$

where $\mathbf{v}_i$ is the image embedding and $\mathbf{t}_i$ is the text embedding of the matching caption. In-batch negatives provide the denominator — exactly the same trick from Section 3.3 of Part 1.

After training, CLIP enables:

- **Image → image search**: Embed query image, find nearest neighbors in image embedding space.
- **Text → image search**: Embed a text query, retrieve images whose embeddings are closest.
- **Zero-shot classification**: Compare an image embedding against text embeddings of class descriptions.

**Training data**: CLIP was trained on 400 million (image, text) pairs scraped from the internet. The scale of weak supervision mirrors the Sentence Transformer story — cheap, abundant, noisy pairs rather than expensive human labels.

### 2.3 Key Image Embedding Models (as of February 2026)

| Model | Organization | Architecture | Embedding Dim | Training Data | Key Feature |
| ----- | ------------ | ------------ | ------------- | ------------- | ----------- |
| CLIP | OpenAI (2021) | ViT + text Transformer | 512–768 | 400M image-text pairs | Cross-modal text-image search |
| SigLIP | Google (2023) | ViT + sigmoid loss | 256–1152 | WebLI (10B+ pairs) | Sigmoid instead of softmax; better scaling |
| DINOv2 | Meta (2023) | ViT | 384–1536 | 142M curated images | Self-supervised (no text); strong visual features |
| EVA-CLIP | BAAI (2023) | ViT-E (4B params) | 1024 | Merged datasets | Largest open CLIP variant |
| BiomedCLIP | Microsoft (2023) | PubMedBERT + ViT | 512 | PMC-15M (biomedical) | Domain-specific for medical images |
| CONCH | Chen et al. (2024) | CoCa architecture | 512 | Pathology image-text pairs | Histopathology-specific |
| UNI | Chen et al. (2024) | ViT-L | 1024 | 100M+ pathology patches | Self-supervised on pathology; no text needed |
| Virchow-2 | Paige AI (2024) | ViT-H | 1280 | 3M+ whole slide images | Largest pathology foundation model |

### 2.4 Medical Imaging and Pathology

Medical image search is one of the highest-impact applications of visual embeddings. The challenge is that medical images differ fundamentally from natural photographs:

- **Gigapixel resolution**: A whole slide image (WSI) in pathology can be 100,000 x 100,000 pixels — far too large for a single ViT forward pass.
- **Fine-grained distinctions**: The difference between benign and malignant tissue can be subtle at the cellular level.
- **Limited labeled data**: Expert pathologist annotations are expensive and scarce.

**How pathology models handle this:**

**Step 1 — Patch-based encoding**: The WSI is divided into small patches (e.g., 256x256 or 512x512 pixels). Each patch is embedded independently using a ViT encoder (UNI, Virchow-2, CONCH).

**Step 2 — Slide-level aggregation**: Patch embeddings are aggregated into a single slide-level embedding using attention-based multiple instance learning (ABMIL) or Transformer-based pooling. This is analogous to mean pooling in Sentence Transformers, but with learned attention weights:

$$
\mathbf{s}_{\text{slide}} = \sum_{k=1}^{K} \alpha_k \, \mathbf{e}_k, \quad \alpha_k = \frac{\exp(w^T \tanh(V \mathbf{e}_k))}{\sum_{j} \exp(w^T \tanh(V \mathbf{e}_j))}
$$

where $\mathbf{e}_k$ is the embedding of patch $k$ and $\alpha_k$ is the learned attention weight.

**Step 3 — Contrastive training**: Models like CONCH use contrastive learning on (pathology image, diagnostic text) pairs from pathology reports — the same CLIP paradigm applied to the medical domain.

**Practical impact**: A pathologist can embed a tissue region and retrieve similar cases from a database of millions of slides. This enables case-based reasoning, rare disease identification, and quality assurance.

---

## 3. Molecular Structure Embeddings

### 3.1 The Representation Challenge

Molecules are not sequences or images — they are **graphs** (atoms as nodes, bonds as edges) with 3D spatial structure. This creates a representation hierarchy:

| Level | Representation | What It Captures |
| ----- | -------------- | ---------------- |
| 1D | SMILES string (e.g., `CC(=O)OC1=CC=CC=C1C(=O)O`) | Atom connectivity as text |
| 2D | Molecular graph (atoms + bonds) | Topology, functional groups |
| 3D | Conformer (atom coordinates in $\mathbb{R}^3$) | Spatial arrangement, binding geometry |

Each level requires a different encoder, and **higher levels capture more information but are harder to obtain and encode**.

### 3.2 SMILES-Based Approaches (1D)

SMILES strings are text, so the Sentence Transformer paradigm applies directly:

- **Tokenizer**: Character-level or BPE on SMILES strings.
- **Encoder**: Transformer (BERT-style) pre-trained with masked language modeling on SMILES corpora.
- **Contrastive pairs**: Molecules with similar bioactivity, same scaffold, or similar fingerprints.

| Model | Approach | Key Feature |
| ----- | -------- | ----------- |
| ChemBERTa | RoBERTa on SMILES | Pre-trained on 77M SMILES from PubChem |
| MolBERT | BERT on SMILES + molecular properties | Multi-task pre-training |
| SELFormer | SMILES + learned fingerprints | Combines sequence and structural features |

**Limitation**: SMILES is a linearization of a graph — the same molecule can have multiple valid SMILES representations, and small string edits can produce radically different molecules. This makes SMILES-based similarity unreliable for some applications.

### 3.3 Graph-Based Approaches (2D)

Graph neural networks (GNNs) operate directly on the molecular graph:

- **Node features**: Atom type, charge, hybridization, etc.
- **Edge features**: Bond type, stereochemistry.
- **Message passing**: Each atom aggregates information from its neighbors over multiple rounds.
- **Graph pooling**: Atom-level representations are pooled into a single molecular embedding (mean, sum, attention, or virtual node).

This is the molecular analogue of Sentence Transformer pooling — collapsing variable-length node representations into a fixed-size vector.

| Model | Architecture | Key Feature |
| ----- | ------------ | ----------- |
| GIN (Graph Isomorphism Network) | Message-passing GNN | Provably as powerful as the WL graph isomorphism test |
| SchNet | Continuous-filter convolution | Incorporates interatomic distances (2D→3D bridge) |
| DimeNet++ | Directional message passing | Uses bond angles, not just distances |
| GEM (Graph-based molecular) | GNN + geometry | Pre-trained on 20M conformers |

**Contrastive training for molecules**: The same InfoNCE framework applies. Positive pairs can be:

- Molecules with the same biological target (activity cliffs).
- Augmented views of the same molecule (atom masking, subgraph removal).
- Molecules with similar Tanimoto fingerprint similarity above a threshold.

### 3.4 3D Conformer Approaches

For drug design and binding prediction, 3D structure matters — two molecules with identical 2D graphs can have different 3D shapes and different biological activity.

3D molecular encoders process atom coordinates directly:

| Model | Input | Architecture | Key Feature |
| ----- | ----- | ------------ | ----------- |
| SchNet | Atom positions + types | Continuous-filter convolution | Distance-based interactions |
| DimeNet++ | Atom positions | Directional message passing | Bond angles and dihedral angles |
| SphereNet | Atom positions | Spherical message passing | Full 3D geometric information |
| Uni-Mol | Atom positions + types | 3D Transformer | Pre-trained on 209M conformers; SoA on multiple benchmarks |
| GeoSSL | Atom positions | GNN + self-supervised | Contrastive + predictive 3D pre-training |

**Uni-Mol** (DP Technology, 2023) deserves special mention as it is among the strongest general-purpose molecular representation models. It uses a 3D Transformer that directly processes atomic coordinates and is pre-trained on a massive conformer dataset with denoising and contrastive objectives.

---

## 4. 3D Object and Surface Embeddings

### 4.1 The General 3D Problem

Beyond molecules, semantic search over arbitrary 3D objects (CAD models, anatomical structures, geological formations) is an active research area. The core challenge: **3D data has no canonical ordering** — unlike text (sequential) or images (grid), 3D objects are unordered sets of points or mesh vertices.

### 4.2 Representations

| Representation | Description | Pros | Cons |
| -------------- | ----------- | ---- | ---- |
| Point cloud | Unordered set of $(x, y, z)$ coordinates | Simple, flexible | No surface/topology info |
| Mesh | Vertices + faces (triangles) | Captures surface | Variable topology |
| Voxel grid | 3D occupancy grid | Regular structure (like 3D images) | Memory-intensive, resolution-limited |
| Multi-view images | 2D renderings from multiple viewpoints | Leverages 2D vision models | Loses interior structure |
| Implicit (NeRF, SDF) | Neural function mapping coordinates to occupancy/distance | Continuous, resolution-free | Expensive to query |

### 4.3 Key Models for 3D Embeddings

**Point cloud encoders:**

| Model | Architecture | Key Feature |
| ----- | ------------ | ----------- |
| PointNet (Qi et al., 2017) | Per-point MLP + max pooling | First deep learning model for raw point clouds; permutation-invariant |
| PointNet++ | Hierarchical PointNet | Local structure via set abstraction layers |
| Point-BERT (2022) | Masked point modeling (BERT-style) | Pre-trained on ShapeNet; transferable 3D features |
| Point-MAE (2022) | Masked autoencoder for point clouds | Self-supervised; reconstructs masked point patches |

**Multi-view approaches:**

- Render the 3D object from $K$ viewpoints.
- Encode each view with a 2D vision model (ViT, ResNet).
- Aggregate view embeddings (max pool, attention).

This is conceptually identical to the pathology slide approach: multiple local views → pooling → single embedding.

**Contrastive learning for 3D:**

- **CrossPoint** (Afham et al., 2022): Contrastive learning between 3D point clouds and their 2D rendered views. Uses InfoNCE to align 3D and 2D representations.
- **ULIP** (Xue et al., 2023): Unifies language, image, and point cloud representations using CLIP-style contrastive training across all three modalities.
- **OpenShape** (Liu et al., 2023): Scales 3D contrastive learning to 876K shapes with text and image alignment.

### 4.4 Protein 3D Structure Embeddings

Protein 3D structures are a special case of 3D objects with rich biological semantics. The challenge is encoding both the **sequence** and the **spatial arrangement** of residues.

| Model | Input | Architecture | Key Feature |
| ----- | ----- | ------------ | ----------- |
| ESM-IF1 | Backbone coordinates | GVP-Transformer | Inverse folding (structure → sequence) |
| GearNet | Residue contact graph | Relational GNN | Multi-relational edges (sequential, spatial, k-NN) |
| SaProt | Foldseek structural tokens + sequence | Transformer | Encodes 3D as a discrete structural alphabet |
| Uni-Mol (protein mode) | Atom coordinates | 3D Transformer | Unified framework for small molecules and proteins |

**SaProt** is particularly elegant: it uses Foldseek to convert 3D structure into a discrete alphabet of structural tokens, then interleaves them with amino acid tokens. This converts the 3D problem into a sequence problem that a standard Transformer can handle — a clever encoding trick that avoids the complexity of geometric neural networks.

---

## 5. Why Similarity Gets Harder in Higher Dimensions

A recurring theme across these domains is that **defining similarity becomes increasingly ambiguous** as the data gets richer:

| Domain | What "similar" means | Ambiguity |
| ------ | -------------------- | --------- |
| Text | Paraphrase, topical overlap | Low — humans agree on text similarity |
| Images | Visual appearance, semantic content | Medium — style vs. content vs. object identity |
| Molecules | Same target, same scaffold, same shape, same activity | High — multiple valid similarity notions |
| 3D objects | Geometric shape, function, category | High — a chair and a stool are functionally similar but geometrically different |
| Protein structures | Fold similarity, functional similarity, binding site similarity | Very high — same fold can have different functions |

This ambiguity means that **the choice of positive pairs during contrastive training implicitly defines what "similarity" means** in the learned embedding space. There is no universal similarity — only task-specific ones.

This is the same insight from Section 3.5 of Part 1 (task-specific vs. general-purpose models), but amplified: in visual and molecular domains, the gap between different similarity notions is even wider than in text.

---

## 6. The Unified View

Across all domains covered in this series, the same architecture recurs:

```text
Domain-specific input
    → Domain-specific encoder (Transformer, GNN, PointNet, ViT)
        → Pooling (mean, CLS, attention, graph readout)
            → Fixed-size embedding in R^d
                → Contrastive loss (InfoNCE)
                    → Metric space where retrieval = nearest neighbor search
```

What varies:

| Component | Text | Image | Molecule | 3D Object |
| --------- | ---- | ----- | -------- | --------- |
| Encoder | BERT, RoBERTa | ViT, ConvNeXt | GNN, 3D Transformer | PointNet, ViT (multi-view) |
| Tokenizer | BPE, WordPiece | Patch embedding | Atom/bond features or SMILES | Point patches or voxels |
| Pooling | Mean over tokens | CLS or mean over patches | Graph readout (sum/mean/attention) | Max pool or set abstraction |
| Positive pairs | Paraphrases, Q&A | (image, caption) | Same target, augmented views | (3D, 2D render), (3D, text) |
| Cross-modal? | Rarely | Yes (CLIP) | Yes (MolCLIP) | Yes (ULIP, OpenShape) |

The loss function — InfoNCE — is **identical across all of them**. The implementation from Part 2 works without modification for any of these domains, provided you swap the encoder.

---

## 7. State of the Art — Summary (as of February 2026)

| Domain | SoA Approach | Maturity | Key Challenge |
| ------ | ------------ | -------- | ------------- |
| Natural images | CLIP, SigLIP, DINOv2 | **Mature** | Scaling data and model size |
| Medical / pathology images | UNI, Virchow-2, CONCH | **Maturing rapidly** | Gigapixel WSIs, limited annotations |
| Molecules (2D graph) | GIN + contrastive pre-training | **Mature** | Multiple valid similarity definitions |
| Molecules (3D conformer) | Uni-Mol, DimeNet++ | **Maturing** | Conformer generation, flexibility |
| 3D objects (point clouds) | Point-MAE, ULIP, OpenShape | **Active research** | No canonical representation |
| Protein 3D structure | SaProt, GearNet, ESM-IF1 | **Maturing** | Bridging sequence and structure |
| Cross-modal (text + image + 3D) | ULIP, OpenShape | **Early** | Alignment across 3+ modalities |

---

## References

### Image Embeddings

- Radford, A., et al. (2021). *Learning Transferable Visual Models From Natural Language Supervision (CLIP)*. ICML 2021.
- Zhai, X., et al. (2023). *Sigmoid Loss for Language Image Pre-Training (SigLIP)*. ICCV 2023.
- Oquab, M., et al. (2023). *DINOv2: Learning Robust Visual Features without Supervision*. TMLR 2024.

### Medical / Pathology

- Zhang, S., et al. (2023). *BiomedCLIP: A Multimodal Biomedical Foundation Model*. arXiv:2303.00915.
- Lu, M.Y., et al. (2024). *A Visual-Language Foundation Model for Computational Pathology (CONCH)*. Nature Medicine.
- Chen, R.J., et al. (2024). *Towards a General-Purpose Foundation Model for Computational Pathology (UNI)*. Nature Medicine.
- Vorontsov, E., et al. (2024). *Virchow: A Million-Slide Digital Pathology Foundation Model*. arXiv:2309.07778.

### Molecular Representations

- Ahmad, W., et al. (2022). *ChemBERTa-2: Towards Chemical Foundation Models*. arXiv:2209.01712.
- Zhou, G., et al. (2023). *Uni-Mol: A Universal 3D Molecular Representation Learning Framework*. ICLR 2023.
- Gasteiger, J., et al. (2022). *GemNet: Universal Directional Graph Neural Networks for Molecules*. NeurIPS 2021.
- Xu, K., et al. (2019). *How Powerful are Graph Neural Networks? (GIN)*. ICLR 2019.

### 3D Objects

- Qi, C.R., et al. (2017). *PointNet: Deep Learning on Point Sets for 3D Classification and Segmentation*. CVPR 2017.
- Pang, Y., et al. (2022). *Masked Autoencoders for Point Cloud Self-supervised Learning (Point-MAE)*. ECCV 2022.
- Xue, L., et al. (2023). *ULIP: Learning a Unified Representation of Language, Images, and Point Clouds*. CVPR 2023.
- Liu, M., et al. (2023). *OpenShape: Scaling Up 3D Shape Representation Towards Open-World Understanding*. NeurIPS 2023.

### Protein 3D Structure

- Hsu, C., et al. (2022). *Learning Inverse Folding from Millions of Predicted Structures (ESM-IF1)*. ICML 2022.
- Zhang, Z., et al. (2023). *A Systematic Study of Joint Representation Learning on Protein Sequences and Structures (GearNet)*. arXiv:2303.06275.
- Su, J., et al. (2024). *SaProt: Protein Language Modeling with Structure-aware Vocabulary*. ICLR 2024.

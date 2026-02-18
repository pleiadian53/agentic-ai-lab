# Biological Sequence Embeddings: From Sentence Transformers to Protein and DNA Models

**How the contrastive metric learning paradigm transfers from natural language to biology.**

Previous parts:

- [Part 1 — How Sentence Transformers Work](./01_how_sentence_transformers_work.md)
- [Part 2 — InfoNCE Loss and Training](./02_infonce_loss_and_training.md)

---

## 1. The Core Analogy

The Sentence Transformer design pattern — **encoder + pooling + contrastive loss** — is not specific to natural language. It applies whenever you need to:

1. Map variable-length inputs to fixed-size vectors.
2. Ensure that semantically similar inputs are geometrically close.
3. Perform retrieval, clustering, or classification downstream.

Biological sequences (DNA, RNA, proteins) satisfy all three requirements. The key insight from Part 1 carries over directly:

> Once you learn a good metric space, retrieval becomes geometry — whether the inputs are English sentences, protein sequences, or gene sets.

What changes across domains is not the architecture but the **tokenizer**, the **pre-training corpus**, and the **definition of similarity**.

| Component | Natural Language | Protein | DNA/RNA |
| --------- | ---------------- | ------- | ------- |
| Input | Sentence / paragraph | Amino acid sequence | Nucleotide sequence |
| Tokenizer | WordPiece / BPE | Per-residue or BPE | k-mer or BPE |
| Pre-training | Masked language modeling on text corpora | Masked LM on UniRef / UniProt | Masked LM on reference genomes |
| Similarity pairs | Paraphrases, Q&A, NLI | Homologs, GO co-annotations | Orthologous regions, regulatory function |
| Embedding dim | 384–768 | 320–5120 | 256–2560 |

---

## 2. Protein Sequence Embeddings

### 2.1 Foundation Models

Protein language models treat amino acid sequences as "sentences" and learn contextual representations through masked language modeling — the same pre-training objective as BERT.

**ESM-2** (Meta AI, 2022) is the dominant protein foundation model as of early 2026:

- Trained on ~65 million protein sequences from UniRef.
- Model sizes range from 8M to 15B parameters.
- Each residue gets a contextual embedding; mean pooling produces a sequence-level vector.
- The learned representations capture structural and functional properties without any explicit structural supervision.

```python
import torch
from transformers import AutoModel, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")
model = AutoModel.from_pretrained("facebook/esm2_t33_650M_UR50D")

sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
inputs = tokenizer(sequence, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)
    # Mean pooling over residue representations (excluding special tokens)
    hidden = outputs.last_hidden_state[:, 1:-1, :]  # remove [CLS] and [EOS]
    embedding = hidden.mean(dim=1)  # [1, 1280]

print(f"Embedding shape: {embedding.shape}")  # torch.Size([1, 1280])
```

This is structurally identical to the `SentenceEncoder` from Part 2 — a transformer backbone followed by mean pooling.

**Other notable protein models:**

| Model | Architecture | Parameters | Training Data | Key Feature |
| ----- | ------------ | ---------- | ------------- | ----------- |
| ESM-2 | Transformer encoder | 8M–15B | UniRef50 | Dominant general-purpose protein LM |
| ProtTrans (ProtT5) | T5 encoder-decoder | Up to 11B | UniRef, BFD | Strong on function prediction |
| ESM-3 | Multimodal (sequence + structure + function) | 1.4B–98B | Sequence + PDB structures | Generates functional proteins |
| SaProt | Structure-aware | 650M | Foldseek structural alphabet + sequence | Uses 3D structure tokens alongside amino acids |

### 2.2 Contrastive Fine-Tuning for Proteins

Pre-trained protein models produce general-purpose embeddings. For specific tasks (e.g., retrieving functionally similar proteins), contrastive fine-tuning improves performance — exactly as Sentence-BERT fine-tunes BERT for text similarity.

Positive pairs for protein contrastive learning:

- **Homologous sequences**: Proteins from the same family (Pfam) or with shared evolutionary origin.
- **GO co-annotations**: Proteins sharing Gene Ontology terms (molecular function, biological process, cellular component).
- **Protein-protein interaction partners**: Proteins known to physically interact (from STRING, BioGRID).
- **Enzyme Commission (EC) co-classification**: Enzymes catalyzing the same reaction type.

The InfoNCE loss from Part 2 applies without modification — the only change is the input domain.

---

## 3. DNA and RNA Sequence Embeddings

### 3.1 Foundation Models

DNA/RNA language models face a unique challenge: the alphabet is small (4 nucleotides: A, C, G, T/U), but the sequences are extremely long (genes span thousands to millions of bases). Tokenization strategy is critical.

**Key models as of early 2026:**

| Model | Organization | Parameters | Context Length | Tokenization | Key Feature |
| ----- | ------------ | ---------- | -------------- | ------------ | ----------- |
| DNABERT-2 | Zhihan Zhou et al. | 117M | 512 tokens | Multi-species BPE | Improved over k-mer DNABERT |
| Nucleotide Transformer | InstaDeep / NVIDIA | Up to 2.5B | 6 kb | 6-mer | Trained on 3,200+ genomes |
| Evo | Arc Institute (2024) | 7B | 131k tokens | Single-nucleotide | StripedHyena (not Transformer); long-range genomic modeling |
| Caduceus | Kuleshov Lab (2024) | 128M–1.5B | Up to 131k | BPE | Bi-directional Mamba; long-range with linear scaling |
| HyenaDNA | Nguyen et al. (2023) | Up to 1.6B | Up to 1M tokens | Single-nucleotide | Hyena operator; ultra-long context |

### 3.2 Tokenization: k-mers vs. BPE vs. Single-Nucleotide

The choice of tokenizer has a significant impact on DNA models:

- **k-mer tokenization** (e.g., DNABERT, Nucleotide Transformer): Splits the sequence into overlapping or non-overlapping subsequences of length $k$. A 6-mer vocabulary has $4^6 = 4{,}096$ tokens. This captures local motifs but introduces a fixed resolution.

- **BPE tokenization** (e.g., DNABERT-2, Caduceus): Learns a data-driven vocabulary from the corpus, similar to text BPE. More flexible than fixed k-mers and handles variable-length patterns.

- **Single-nucleotide tokenization** (e.g., Evo, HyenaDNA): Each base is one token. Maximally fine-grained but requires architectures that handle very long sequences efficiently (hence Hyena/Mamba instead of standard Transformers).

### 3.3 Relevance to Splice Site Prediction

For projects like splice site prediction (e.g., SpliceAI-style models), DNA embeddings from foundation models can serve as:

- **Feature extractors**: Replace hand-crafted sequence features with learned representations from DNABERT-2 or Nucleotide Transformer.
- **Transfer learning backbones**: Fine-tune a pre-trained DNA model on splice site classification, analogous to fine-tuning BERT for text classification.
- **Retrieval indices**: Embed genomic regions and retrieve similar splice contexts for comparative analysis.

The contrastive learning framework applies here too: positive pairs could be orthologous splice sites across species, or splice sites with similar regulatory contexts.

---

## 4. Gene Set and Pathway Embeddings

Pathways involving multiple genes present a different challenge: a pathway is a **set or graph of genes**, not a linear sequence. You cannot simply concatenate gene names and embed them as a "sentence."

### 4.1 Approaches

**Set-based (bag-of-genes) embeddings:**

The simplest approach treats a pathway as a set of gene embeddings and aggregates them:

$$
\mathbf{p} = \text{Pool}\!\big(\{e_{g_1}, e_{g_2}, \dots, e_{g_k}\}\big)
$$

where $e_{g_i}$ is the embedding of gene $g_i$ (from ESM-2, scGPT, or a gene expression model) and Pool is mean, max, or attention-weighted pooling. This is the direct analogue of Sentence Transformers — and it works for coarse pathway similarity but **loses interaction structure**.

**Graph-based embeddings:**

Pathways have topology: genes activate, inhibit, or co-regulate each other. Graph neural networks (GNNs) preserve this structure:

- Nodes = genes (initialized with gene embeddings or expression features).
- Edges = interactions (from KEGG, Reactome, STRING, BioGRID).
- A GNN (e.g., GraphSAGE, GAT, GIN) produces a pathway-level embedding via graph pooling.

This is more expressive than set-based approaches but requires curated interaction graphs.

**Contrastive learning on gene sets:**

Recent work applies InfoNCE-style losses to gene set representations:

- **Positive pairs**: Pathways with overlapping biological function (shared GO terms, same disease association).
- **Negative pairs**: In-batch negatives from unrelated pathways.
- **Encoder**: Set transformer or GNN.

This is conceptually identical to Sentence Transformer training — the loss function is the same, only the encoder and data domain change.

### 4.2 Key Models for Gene-Level Embeddings

| Model | Domain | Approach | Key Feature |
| ----- | ------ | -------- | ----------- |
| scGPT | Single-cell transcriptomics | Transformer on gene expression profiles | Learns cell-level and gene-level embeddings |
| Geneformer | Single-cell transcriptomics | Rank-value encoding of gene expression | Pre-trained on ~30M single-cell profiles |
| Gene2Vec | Gene co-expression | Word2Vec-style on gene co-expression | Lightweight; captures co-expression patterns |
| scFoundation | Single-cell | Large-scale foundation model (100M+ cells) | Asymmetric encoder-decoder |

These models produce gene-level embeddings that can be aggregated into pathway embeddings using the set-based or graph-based approaches described above.

### 4.3 Current Limitations

- **No dominant method**: Unlike protein embeddings (where ESM-2 is a clear leader), pathway embedding is fragmented across different databases, evaluation benchmarks, and modeling choices.
- **Graph quality matters**: GNN-based approaches are only as good as the underlying interaction graph. Incomplete or noisy edges degrade performance.
- **Scale mismatch**: Gene set sizes vary enormously (from 3 genes to 300+), making fixed-size pooling strategies lossy for large pathways.

---

## 5. The Unifying Pattern

Across all these domains, the same design pattern recurs:

```text
Domain-specific tokenizer
    → Transformer (or SSM) encoder
        → Pooling (mean, CLS, attention, graph)
            → Fixed-size embedding in R^d
                → Contrastive loss (InfoNCE, triplet, etc.)
```

The **loss function** (InfoNCE from Part 2) is domain-agnostic. The **encoder architecture** and **tokenizer** are domain-specific. The **similarity definition** (what counts as a positive pair) encodes domain knowledge.

This modularity is why the Sentence Transformer paradigm has spread so broadly: you can swap components independently without redesigning the system.

---

## 6. State of the Art — Summary (as of February 2026)

| Domain | SoA Approach | Maturity |
| ------ | ------------ | -------- |
| Protein sequences | ESM-2/ESM-3 embeddings + contrastive fine-tuning | **Mature** — widely adopted, strong benchmarks |
| DNA/RNA sequences | DNABERT-2, Nucleotide Transformer, Evo | **Maturing** — rapid progress, long-context models emerging |
| Splice site prediction | DNA foundation models as feature extractors + task-specific heads | **Active** — transfer learning from DNA LMs showing promise |
| Gene sets / pathways | Set pooling or GNNs over gene embeddings + contrastive loss | **Early** — no dominant method, fragmented evaluation |
| Single-cell gene expression | scGPT, Geneformer, scFoundation | **Maturing** — foundation models gaining traction |

The contrastive metric learning paradigm is **at or near SoA for individual sequences** (protein, DNA). For pathways and gene sets, it is a **competitive approach but not yet settled** — the field is still exploring the right combination of encoder, graph structure, and training signal.

---

## References

- Lin, Z., et al. (2023). *Evolutionary-scale prediction of atomic-level protein structure with a language model (ESM-2)*. Science, 379(6637).
- Hayes, T., et al. (2024). *Simulating 500 million years of evolution with a language model (ESM-3)*. bioRxiv.
- Zhou, Z., et al. (2024). *DNABERT-2: Efficient Foundation Model and Benchmark for Multi-Species Genome*. ICLR 2024.
- Dalla-Torre, H., et al. (2023). *The Nucleotide Transformer: Building and Evaluating Robust Foundation Models for Human Genomics*. bioRxiv.
- Nguyen, E., et al. (2024). *Sequence modeling and design from molecular to genome scale with Evo*. Science, 386(6723).
- Nguyen, E., et al. (2023). *HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution*. NeurIPS 2023.
- Schiff, Y., et al. (2024). *Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling*. ICML 2024.
- Cui, H., et al. (2024). *scGPT: Toward Building a Foundation Model for Single-Cell Multi-omics Using Generative AI*. Nature Methods.
- Theodoris, C.V., et al. (2023). *Transfer learning enables predictions in network biology (Geneformer)*. Nature.
- Su, J., et al. (2024). *SaProt: Protein Language Modeling with Structure-aware Vocabulary*. ICLR 2024.
- Elnaggar, A., et al. (2022). *ProtTrans: Toward Understanding the Language of Life Through Self-Supervised Learning*. IEEE TPAMI.
- Du, J., et al. (2019). *Gene2vec: Distributed Representation of Genes Based on Co-Expression*. BMC Genomics.

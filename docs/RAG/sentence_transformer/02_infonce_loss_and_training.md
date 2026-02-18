# Implementing InfoNCE Loss for Contrastive Training

**A code-first tutorial on designing a contrastive loss function and using it to train a sentence encoder.**

Companion code: [`infonce_training_example.py`](./infonce_training_example.py)

---

## 1. Motivation

In [Part 1](./01_how_sentence_transformers_work.md), we saw that Sentence Transformers learn a semantic embedding space through contrastive training. The core loss function is **InfoNCE** — but what does it actually look like in code, and how does it connect to the standard PyTorch training loop?

This tutorial walks through a from-scratch implementation to answer a practical question:

> **How do you design a loss function that teaches a model to place similar texts nearby and dissimilar texts far apart?**

---

## 2. The InfoNCE Loss — From Math to Code

### 2.1 The Objective

Given a batch of $N$ anchor-positive pairs $(a_i, p_i)$, the InfoNCE loss for anchor $a_i$ is:

$$
\mathcal{L}_i = -\log \frac{\exp\!\big(\text{sim}(a_i, p_i) / \tau\big)}{\displaystyle\sum_{j=1}^{N} \exp\!\big(\text{sim}(a_i, p_j) / \tau\big)}
$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity and $\tau > 0$ is a temperature parameter.

**Key insight**: The denominator sums over *all* positives in the batch. For anchor $a_i$, the correct positive is $p_i$ (the numerator), while every other $p_j$ ($j \neq i$) acts as a negative. This is the **in-batch negatives** trick — no explicit negative mining needed.

### 2.2 Why This Is Just Cross-Entropy

The loss has a clean interpretation. Consider the $N \times N$ similarity matrix:

$$
S_{ij} = \frac{\text{sim}(a_i, p_j)}{\tau}
$$

Each row $i$ is a logit vector over $N$ "classes." The correct class for row $i$ is column $i$ (the true positive). So InfoNCE is equivalent to:

$$
\mathcal{L} = \text{CrossEntropy}(S, \;\text{labels} = [0, 1, 2, \dots, N{-}1])
$$

This is exactly how the implementation works.

### 2.3 The Implementation

From [`infonce_training_example.py`](./infonce_training_example.py), lines 29-82:

```python
class InfoNCELoss(nn.Module):
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, anchor_embeds, positive_embeds):
        # Step 1: L2-normalize so dot product == cosine similarity
        anchor_embeds = F.normalize(anchor_embeds, p=2, dim=1)
        positive_embeds = F.normalize(positive_embeds, p=2, dim=1)

        # Step 2: All-pairs cosine similarity matrix [N, N]
        similarity = torch.matmul(anchor_embeds, positive_embeds.T) / self.temperature

        # Step 3: Labels — diagonal entries are the positive pairs
        labels = torch.arange(similarity.size(0), device=similarity.device)

        # Step 4: Cross-entropy over the similarity matrix
        loss = F.cross_entropy(similarity, labels)
        return loss
```

Four steps, each mapping directly to the math:

| Step | Math | Code |
| ---- | ---- | ---- |
| Normalize | $\hat{a}_i = a_i / \|a_i\|$ | `F.normalize(anchor_embeds, p=2, dim=1)` |
| Similarity matrix | $S_{ij} = \hat{a}_i \cdot \hat{p}_j / \tau$ | `torch.matmul(...) / self.temperature` |
| Labels | Correct class for row $i$ is $i$ | `torch.arange(N)` |
| Loss | $-\log \text{softmax}(S_i)_i$ | `F.cross_entropy(similarity, labels)` |

### 2.4 The Role of Temperature

The temperature $\tau$ controls the sharpness of the softmax distribution:

- **Small $\tau$** (e.g., 0.05): The model must be very confident — small similarity differences produce large logit differences. Harder to optimize but learns finer distinctions.
- **Large $\tau$** (e.g., 1.0): The distribution is smoother. Easier to optimize but less discriminative.

The default $\tau = 0.07$ is a common choice in the literature (used by SimCLR, CLIP, and many Sentence Transformer models).

---

## 3. The Sentence Encoder

The encoder is a standard pattern: **transformer backbone + mean pooling**.

From [`infonce_training_example.py`](./infonce_training_example.py), lines 89-131:

```python
class SentenceEncoder(nn.Module):
    def __init__(self, model_name="bert-base-uncased"):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)

    def mean_pool(self, hidden_states, attention_mask):
        mask = attention_mask.unsqueeze(-1).float()
        summed = (hidden_states * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        return summed / counts

    def forward(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state
        return self.mean_pool(hidden_states, attention_mask)
```

### Why mean pooling needs the attention mask

Batched inputs are padded to equal length. Without masking, the padding tokens (which have meaningless hidden states) would pollute the average. The mask ensures only real tokens contribute:

$$
\mathbf{s} = \frac{\sum_{t=1}^{T} m_t \cdot h_t}{\sum_{t=1}^{T} m_t}
$$

where $m_t \in \{0, 1\}$ is the attention mask for token $t$.

---

## 4. The Training Loop

The training loop follows the standard PyTorch pattern, with one key difference: **each batch produces two forward passes** (one for anchors, one for positives).

From [`infonce_training_example.py`](./infonce_training_example.py), lines 178-200:

```python
def train_one_epoch(model, dataloader, optimizer, loss_fn, device):
    model.train()
    total_loss = 0.0
    for batch in dataloader:
        # Encode anchors and positives
        anchor_embeds = model(batch["anchor_input_ids"], batch["anchor_attention_mask"])
        positive_embeds = model(batch["positive_input_ids"], batch["positive_attention_mask"])

        # InfoNCE loss — in-batch negatives are implicit
        loss = loss_fn(anchor_embeds, positive_embeds)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)
```

### What the gradient is actually doing

When `loss.backward()` runs, the gradient flows through:

1. `F.cross_entropy` — pushes the diagonal of the similarity matrix up (positive pairs) and off-diagonal entries down (negative pairs).
2. `torch.matmul` — propagates to the embedding vectors.
3. `mean_pool` — distributes the gradient across token representations.
4. `backbone` (BERT) — updates the transformer weights so that similar texts produce similar token representations.

The entire model — from tokenization to embedding — is trained end-to-end by this single loss.

---

## 5. Design Patterns to Notice

This example illustrates several general patterns for designing contrastive training systems:

### 5.1 Loss design as a similarity matrix problem

Many contrastive losses (InfoNCE, NT-Xent, CLIP) share the same structure:

1. Compute a pairwise similarity matrix.
2. Define which entries are "correct" (positive pairs).
3. Apply cross-entropy (or a margin-based loss) to push correct entries above incorrect ones.

If you understand this pattern, you can read and implement most contrastive losses.

### 5.2 In-batch negatives as free supervision

A batch of $N$ pairs gives $N$ positives and $N(N-1)$ negatives. This quadratic scaling is why contrastive learning works with relatively small labeled datasets — the batch itself generates most of the training signal.

### 5.3 Normalization before similarity

L2-normalizing embeddings before computing dot products ensures that:

- The dot product equals cosine similarity (bounded in $[-1, 1]$).
- No single dimension dominates the similarity score.
- The temperature parameter has a consistent effect regardless of embedding magnitude.

### 5.4 Shared encoder for anchors and positives

Both anchors and positives pass through the **same** encoder (shared weights). This is the Siamese architecture. It ensures that the embedding space is consistent — the same text always maps to the same vector regardless of whether it appears as an anchor or a positive.

---

## 6. Running the Example

```bash
mamba run -n agentic-ai python docs/RAG/sentence_transformer/infonce_training_example.py
```

Expected output:

```text
Device: cpu
Training for 3 epochs on 8 pairs...
Batch size: 4  |  In-batch negatives per anchor: 3
--------------------------------------------------
Epoch 1/3  |  Loss: X.XXXX
Epoch 2/3  |  Loss: X.XXXX
Epoch 3/3  |  Loss: X.XXXX

==================================================
Inference: encoding new sentences
==================================================
  "Renewable energy is the future."
    shape: torch.Size([1, 768])  |  norm: 1.0000
  ...

==================================================
Pairwise cosine similarities
==================================================
  sim("Renewable energy is the future.", "Wind turbines produce clean electricity.") = 0.XXXX
  sim("Renewable energy is the future.", "The cat sat on the mat.") = 0.XXXX
  ...
```

The loss should decrease across epochs. After training, semantically related sentences (renewable energy, wind turbines) should have higher cosine similarity than unrelated ones (energy vs. cat).

---

## 7. What This Example Does *Not* Cover

This is a minimal demonstration. Production Sentence Transformer training additionally involves:

- **Hard negative mining**: Selecting negatives that are close but not identical to the anchor, which provides stronger gradient signal than random negatives.
- **Multi-task training**: Combining InfoNCE with other losses (e.g., cosine similarity regression on STS benchmarks).
- **Large-scale data**: Training on millions of pairs from diverse sources (see Section 3.4 of [Part 1](./01_how_sentence_transformers_work.md)).
- **Matryoshka Representation Learning (MRL)**: Training embeddings that are useful at multiple dimensionalities.
- **Evaluation**: Measuring retrieval quality with metrics like MRR, NDCG, and recall@k.

These are topics for future tutorials.

---

## References

- Oord, A. van den, Li, Y., & Vinyals, O. (2018). *Representation Learning with Contrastive Predictive Coding*. arXiv:1807.03748.
- Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). *A Simple Framework for Contrastive Learning of Visual Representations (SimCLR)*. ICML 2020.
- Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019.
- Radford, A., et al. (2021). *Learning Transferable Visual Models From Natural Language Supervision (CLIP)*. ICML 2021.

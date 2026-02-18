"""
InfoNCE Contrastive Loss — Implementation and Training Example

Demonstrates how to:
1. Implement the InfoNCE loss from scratch
2. Build a simple sentence encoder (pooling on top of a transformer)
3. Train the encoder with in-batch negatives on synthetic data

This script is designed to be read alongside the companion tutorial:
    docs/RAG/sentence_transformer/02_infonce_loss_and_training.md

Usage:
    mamba run -n agentic-ai python docs/RAG/sentence_transformer/infonce_training_example.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer
from torch.utils.data import DataLoader, Dataset


# ---------------------------------------------------------------------------
# 1. InfoNCE Loss
# ---------------------------------------------------------------------------

class InfoNCELoss(nn.Module):
    """
    InfoNCE (Noise-Contrastive Estimation) loss for contrastive learning.

    Given a batch of (anchor, positive) embedding pairs, this loss treats
    every other positive in the batch as a negative for each anchor.

    For anchor embedding a_i and positive embedding p_i:

        L_i = -log( exp(sim(a_i, p_i) / tau) / sum_j exp(sim(a_i, p_j) / tau) )

    where sim is cosine similarity and tau is a temperature parameter.

    Args:
        temperature: Scaling factor for the similarity scores. Lower values
                     make the distribution sharper (more confident). Default: 0.07.
    """

    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, anchor_embeds: torch.Tensor, positive_embeds: torch.Tensor) -> torch.Tensor:
        """
        Compute the InfoNCE loss.

        Args:
            anchor_embeds:   [batch_size, embed_dim] — L2-normalized anchor embeddings.
            positive_embeds: [batch_size, embed_dim] — L2-normalized positive embeddings.

        Returns:
            Scalar loss (mean over the batch).
        """
        # Step 1: L2-normalize so dot product == cosine similarity
        anchor_embeds = F.normalize(anchor_embeds, p=2, dim=1)
        positive_embeds = F.normalize(positive_embeds, p=2, dim=1)

        # Step 2: Compute all-pairs cosine similarity matrix
        # similarity[i, j] = cos(anchor_i, positive_j)
        # Shape: [batch_size, batch_size]
        similarity = torch.matmul(anchor_embeds, positive_embeds.T) / self.temperature

        # Step 3: The diagonal entries are the positive pairs (i, i).
        # We want each row's diagonal entry to have the highest score.
        # This is equivalent to a cross-entropy loss where the "correct class"
        # for row i is column i.
        labels = torch.arange(similarity.size(0), device=similarity.device)

        # Step 4: Cross-entropy over the similarity matrix
        # This is exactly the InfoNCE objective.
        loss = F.cross_entropy(similarity, labels)

        return loss


# ---------------------------------------------------------------------------
# 2. Sentence Encoder: Transformer + Mean Pooling
# ---------------------------------------------------------------------------

class SentenceEncoder(nn.Module):
    """
    A minimal sentence encoder: a pre-trained transformer backbone followed
    by mean pooling over token representations.

    This is the same architecture used by SentenceTransformer models.

    Args:
        model_name: HuggingFace model identifier (e.g., "bert-base-uncased").
    """

    def __init__(self, model_name: str = "bert-base-uncased"):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        self.hidden_dim = self.backbone.config.hidden_size

    def mean_pool(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Mean pooling: average token embeddings, ignoring padding tokens.

        Args:
            hidden_states:  [batch_size, seq_len, hidden_dim]
            attention_mask: [batch_size, seq_len] — 1 for real tokens, 0 for padding.

        Returns:
            Sentence embeddings: [batch_size, hidden_dim]
        """
        # Expand mask to match hidden_states shape: [batch_size, seq_len, 1]
        mask = attention_mask.unsqueeze(-1).float()

        # Zero out padding positions, then sum
        summed = (hidden_states * mask).sum(dim=1)        # [batch_size, hidden_dim]
        counts = mask.sum(dim=1).clamp(min=1e-9)          # [batch_size, 1]

        return summed / counts

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Encode a batch of tokenized texts into sentence embeddings.

        Returns:
            Sentence embeddings: [batch_size, hidden_dim]
        """
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state  # [batch_size, seq_len, hidden_dim]
        return self.mean_pool(hidden_states, attention_mask)


# ---------------------------------------------------------------------------
# 3. Dataset: Sentence Pairs
# ---------------------------------------------------------------------------

class SentencePairDataset(Dataset):
    """
    A dataset of (anchor, positive) sentence pairs.

    In practice, these come from sources like:
    - Duplicate questions (StackOverflow, Quora)
    - Title-body pairs (Reddit, Wikipedia)
    - NLI entailment pairs
    - Parallel translations

    Here we use synthetic examples for demonstration.
    """

    def __init__(self, pairs: list[tuple[str, str]], tokenizer, max_length: int = 128):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        anchor_text, positive_text = self.pairs[idx]
        anchor_enc = self.tokenizer(
            anchor_text, padding="max_length", truncation=True,
            max_length=self.max_length, return_tensors="pt"
        )
        positive_enc = self.tokenizer(
            positive_text, padding="max_length", truncation=True,
            max_length=self.max_length, return_tensors="pt"
        )
        return {
            "anchor_input_ids": anchor_enc["input_ids"].squeeze(0),
            "anchor_attention_mask": anchor_enc["attention_mask"].squeeze(0),
            "positive_input_ids": positive_enc["input_ids"].squeeze(0),
            "positive_attention_mask": positive_enc["attention_mask"].squeeze(0),
        }


# ---------------------------------------------------------------------------
# 4. Training Loop
# ---------------------------------------------------------------------------

def train_one_epoch(model, dataloader, optimizer, loss_fn, device):
    """Train the encoder for one epoch and return the average loss."""
    model.train()
    total_loss = 0.0

    for batch in dataloader:
        # Move to device
        a_ids = batch["anchor_input_ids"].to(device)
        a_mask = batch["anchor_attention_mask"].to(device)
        p_ids = batch["positive_input_ids"].to(device)
        p_mask = batch["positive_attention_mask"].to(device)

        # Forward pass: encode both anchors and positives
        anchor_embeds = model(a_ids, a_mask)
        positive_embeds = model(p_ids, p_mask)

        # Compute InfoNCE loss
        loss = loss_fn(anchor_embeds, positive_embeds)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)


# ---------------------------------------------------------------------------
# 5. Main: Putting It All Together
# ---------------------------------------------------------------------------

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # --- Synthetic training data (anchor, positive) pairs ---
    # In practice, these would be mined from real corpora.
    train_pairs = [
        ("Electric vehicles reduce carbon emissions.",
         "EVs help lower greenhouse gas output."),
        ("The stock market rallied on strong earnings.",
         "Equities surged after positive quarterly results."),
        ("Python is a popular programming language.",
         "Python is widely used in software development."),
        ("The patient was diagnosed with pneumonia.",
         "Doctors identified a lung infection in the patient."),
        ("Solar panels convert sunlight into electricity.",
         "Photovoltaic cells generate power from the sun."),
        ("The team won the championship game.",
         "They claimed victory in the final match."),
        ("Machine learning models require large datasets.",
         "Training ML systems needs substantial amounts of data."),
        ("The restaurant serves excellent Italian cuisine.",
         "This place has outstanding Italian food."),
    ]

    # --- Model and tokenizer ---
    model_name = "bert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    encoder = SentenceEncoder(model_name).to(device)

    # --- Loss and optimizer ---
    loss_fn = InfoNCELoss(temperature=0.07)
    optimizer = torch.optim.AdamW(encoder.parameters(), lr=2e-5)

    # --- DataLoader ---
    dataset = SentencePairDataset(train_pairs, tokenizer, max_length=64)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

    # --- Training ---
    num_epochs = 3
    print(f"\nTraining for {num_epochs} epochs on {len(train_pairs)} pairs...")
    print(f"Batch size: {dataloader.batch_size}  |  "
          f"In-batch negatives per anchor: {dataloader.batch_size - 1}")
    print("-" * 50)

    for epoch in range(1, num_epochs + 1):
        avg_loss = train_one_epoch(encoder, dataloader, optimizer, loss_fn, device)
        print(f"Epoch {epoch}/{num_epochs}  |  Loss: {avg_loss:.4f}")

    # --- Inference demo ---
    print("\n" + "=" * 50)
    print("Inference: encoding new sentences")
    print("=" * 50)

    test_sentences = [
        "Renewable energy is the future.",
        "Wind turbines produce clean electricity.",
        "The cat sat on the mat.",
    ]

    encoder.eval()
    with torch.no_grad():
        for sent in test_sentences:
            enc = tokenizer(sent, return_tensors="pt", padding=True, truncation=True, max_length=64)
            emb = encoder(enc["input_ids"].to(device), enc["attention_mask"].to(device))
            emb = F.normalize(emb, p=2, dim=1)
            print(f"  \"{sent}\"")
            print(f"    shape: {emb.shape}  |  norm: {emb.norm().item():.4f}")

    # --- Similarity comparison ---
    print("\n" + "=" * 50)
    print("Pairwise cosine similarities")
    print("=" * 50)

    encoder.eval()
    with torch.no_grad():
        embeddings = []
        for sent in test_sentences:
            enc = tokenizer(sent, return_tensors="pt", padding=True, truncation=True, max_length=64)
            emb = encoder(enc["input_ids"].to(device), enc["attention_mask"].to(device))
            emb = F.normalize(emb, p=2, dim=1)
            embeddings.append(emb)

        embeddings = torch.cat(embeddings, dim=0)  # [3, hidden_dim]
        sim_matrix = torch.matmul(embeddings, embeddings.T)

        for i in range(len(test_sentences)):
            for j in range(i + 1, len(test_sentences)):
                print(f"  sim(\"{test_sentences[i][:40]}...\",")
                print(f"      \"{test_sentences[j][:40]}...\") = {sim_matrix[i, j].item():.4f}")
                print()


if __name__ == "__main__":
    main()

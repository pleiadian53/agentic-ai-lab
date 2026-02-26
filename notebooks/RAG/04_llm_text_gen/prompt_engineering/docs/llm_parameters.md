# LLM Sampling Parameters: Temperature and Top-p

When calling a language model, two parameters — **temperature** and **top-p** — govern how the
model selects its output tokens. Understanding them precisely makes it possible to tune generation
quality for different task types: factual retrieval, creative writing, structured output, and so on.

---

## 1. Temperature

Temperature controls how **random vs. deterministic** the model is when selecting the next token.

### 1.1 The Mechanics

At each generation step, the model scores every token in its vocabulary and converts those raw
scores (logits) to a probability distribution via **softmax**. Temperature $T$ is injected
directly into that softmax:

$$
P(\text{token}_i) = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}
$$

where $z_i$ is the raw logit for token $i$.

Dividing each logit by $T$ reshapes the distribution before sampling:

| $T$ | Effect on distribution | Behavior |
|---|---|---|
| $T \to 0$ | Logits $\to \pm\infty$; distribution collapses to a single spike | Always picks the highest-probability token (greedy decoding) |
| $T = 1.0$ | No change — model probabilities used as-is | The model's natural, unmodified output |
| $T > 1.0$ | Logits shrink toward zero; distribution flattens | Low-probability tokens gain a larger share of the mass |
| $T \to \infty$ | All logits $\to 0$; distribution becomes uniform | Tokens sampled nearly at random from the whole vocabulary |

> **Key intuition:** temperature acts like a "sharpness" dial on the distribution.
> Low $T$ sharpens it to a near-spike; high $T$ smooths it toward uniform.

### 1.2 Practical Range

Temperature is mathematically unbounded above zero — any positive float is valid. In practice:

- Most APIs (Together AI, OpenAI) **cap temperature at 2.0** and return an error beyond that.
- Values above **~2.0** produce increasingly incoherent output; the distribution is so flat that
  nonsensical tokens become likely.
- The **useful creative range** is roughly **0.7–1.3** for most generative tasks.

### 1.3 Reading `temperature = 1.1`

A value of 1.1 is only slightly above the natural baseline of 1.0 — a **mild creativity boost**.
The distribution is marginally flatter, so the model occasionally ventures past the single most
expected word without losing coherence. This is appropriate for open-ended tasks (travel
recommendations, brainstorming, storytelling) where predictable, formulaic output is undesirable.

---

## 2. Top-p (Nucleus Sampling)

Top-p is a **vocabulary filtering** parameter. Rather than reshaping the entire probability
distribution (as temperature does), it discards the long tail of low-probability tokens before
sampling begins.

### 2.1 The Mechanics

Given the probability distribution over the vocabulary at each step:

1. Sort all tokens by probability, highest first.
2. Accumulate probability mass walking down the sorted list.
3. Stop at the smallest set $V$ whose cumulative mass meets or exceeds $p$:

$$
V = \arg\min_{S} \left\{ \sum_{i \in S} P(\text{token}_i) \geq p \right\}
$$

4. Sample only from $V$ — all tokens below the cutoff are excluded.

This set $V$ is the **nucleus** that gives the method its name.

| top-p | Nucleus size | Behavior |
|---|---|---|
| **0.1** | Very tight — only the few most certain tokens | Near-deterministic; only the model's top candidates |
| **0.4** | Moderate — a reasonable spread of plausible tokens | Constrained creativity |
| **0.5** | Half the cumulative probability mass | Moderate diversity |
| **1.0** | All tokens included | Top-p filtering effectively disabled |

Top-p is bounded to **[0.0, 1.0]** since it is a cumulative probability threshold.

---

## 3. How Temperature and Top-p Interact

The two parameters operate at different stages of the sampling pipeline:

```
Logits  →  [temperature reshapes distribution]  →  [top-p filters vocabulary]  →  sample
```

Temperature determines *how flat or sharp* the distribution is. Top-p determines *how large the
candidate set* is. Applying both gives independent control over each axis.

### 3.1 Parameter Choices by Task Type

The `answer_query` function in `C1M4_Ungraded_Lab_2.ipynb` illustrates three archetypal
configurations:

```python
# Technical query (e.g., "What is Pi-hole?")
# → Near-greedy. Only near-certain tokens are candidates.
# → Produces factual, consistent, repeatable answers.
generate_params_dict(query, temperature=0, top_p=0.1)

# Creative query (e.g., "Suggest three places to visit in South America")
# → Slightly flattened distribution; moderate nucleus.
# → The flattening (temperature) makes less-obvious words more competitive;
#   the nucleus (top-p) prevents truly nonsensical tokens from sneaking in.
# → Produces varied yet coherent output.
generate_params_dict(query, temperature=1.1, top_p=0.4)

# Inconclusive / fallback
# → Balanced midpoint on both axes.
generate_params_dict(query, temperature=0.5, top_p=0.5)
```

### 3.2 The Safety-Net Role of Top-p with High Temperature

When temperature is raised above 1.0, the distribution flattens and low-probability tokens
become more likely. Without top-p, this can allow truly improbable (and incoherent) tokens into
the sample. Top-p acts as a **guardrail**: even at `temperature=1.1`, setting `top_p=0.4` ensures
that only tokens from the top 40% of the probability mass are ever sampled, keeping output
coherent.

---

## 4. Summary

| Parameter | Controls | Range | Typical values |
|---|---|---|---|
| `temperature` | Sharpness of the probability distribution | $(0, 2.0]$ in practice | `0` (deterministic) · `0.7–1.0` (balanced) · `1.1–1.3` (creative) |
| `top_p` | Size of the candidate token vocabulary | $[0.0, 1.0]$ | `0.1` (tight) · `0.4–0.6` (moderate) · `1.0` (disabled) |

> **Rule of thumb:** for factual or structured tasks, lower both. For creative or generative
> tasks, raise temperature moderately and set top-p to a mid-range value to maintain coherence.
> Avoid raising temperature without a top-p ceiling.

---

*Document created: 2026-02-20 · Context: `C1M4_Ungraded_Lab_2.ipynb` (Prompt Engineering) ·
Model: `meta-llama/Llama-3.2-3B-Instruct-Turbo` via Together AI*

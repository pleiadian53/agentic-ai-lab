# Customer Service Agent Documentation

This document provides higher-level guidance and examples for the
`multiagent.customer_service` package.

- How to customize prompts.
- How to select a data backend (TinyDB vs DuckDB; SQLite later).
- Example prompts, including "happy path" and invalid/off-topic
  requests.

---

## 1. Entry Points and Roles

### 1.1 `single_agent.py`

`single_agent.py` defines the **main entrypoint** for the
single-agent, code-as-plan workflow:

- `customer_service_agent(question, store, ...)`
  - Orchestrates: prompt building → LLM planning → code execution.
  - Returns structured artifacts (answer, logs, code, table snapshots).

It is not a CLI script by itself; instead, you import and call it from
notebooks, scripts, or other agents. If you want a dedicated
command-line driver, you can add a small `cli_single.py` that wraps
`customer_service_agent(...)`.

---

## 2. Customizing Prompts

The planning prompt is configured via `PromptConfig`:

- Located in `prompt_config.py`.
- Used by `planning.generate_llm_code(...)`.

### 2.1 Modes

Currently, a single field controls the overall style:

- `mode="full"` (default) – detailed spec mirroring the lab notebook.
- `mode="minimal"` – shorter prompt that keeps the key contracts
  (STATUS, answer_text, execute tags) but reduces prose.

Example:

```python
from openai import OpenAI
from multiagent.customer_service.prompt_config import PromptConfig
from multiagent.customer_service.planning import generate_llm_code

client = OpenAI()
cfg = PromptConfig(mode="minimal")

content = generate_llm_code(
    prompt="Return 2 Aviator sunglasses.",
    inventory_tbl=inventory_tbl,
    transactions_tbl=transactions_tbl,
    model="o4-mini",
    temperature=0.5,
    client=client,
    prompt_config=cfg,
)
```

You can add new modes in the future (e.g., `"strict"`,
`"experiment_v2"`) by extending `PromptConfig` and the
`build_customer_service_prompt(...)` builder.

### 2.2 Using PromptConfig implicitly

`customer_service_agent(...)` uses the planning module internally. If
you want it to use a specific prompt mode, the simplest pattern is to
wrap or fork `customer_service_agent` and pass a `PromptConfig` down to
`generate_llm_code`. The current implementation keeps the notebook
semantics (`mode="full"`), which is ideal for reproducibility.

---

## 3. Choosing a Data Backend

The agent uses a `CustomerServiceStore` abstraction to access data.
Three implementations are provided:

- `TinyDBStore`
  - TinyDB-based JSON document store (current single-agent backend).
  - Works with the existing code-as-plan executor.
- `DuckDBStore`
  - Uses pandas DataFrames registered into a DuckDB connection.
  - Useful for SQL or DataFrame-based tools-only / multi-agent workflows.
- `SQLiteStore`
  - File-backed SQL database (for future, more production-like flows).

### 3.1 TinyDB (default for single-agent)

```python
from openai import OpenAI
from multiagent.customer_service import TinyDBStore, customer_service_agent

client = OpenAI()
store = TinyDBStore("store_db.json")

question = "I want to buy 3 pairs of classic sunglasses and 1 pair of aviator sunglasses."

result = customer_service_agent(
    question,
    store=store,
    model="o4-mini",
    temperature=1.0,
    reseed=True,
    client=client,
)

print("ANSWER:", result["exec"]["answer"])
```

### 3.2 DuckDB (for future multi-agent / tools-only)

The single-agent executor expects TinyDB tables, so `DuckDBStore` is
primarily for new executors that work with SQL or DataFrames. Example
initialization:

```python
from multiagent.customer_service import DuckDBStore

store = DuckDBStore()          # in-memory DuckDB
inv_rows = store.get_inventory_rows()
```

You can then build tools that query `store._con` (DuckDB connection)
using SQL, or operate directly on the pandas DataFrames returned by
`get_raw_handles()`.

---

## 4. Example Prompts

This section sketches input prompts and expected qualitative behavior.
Exact wording and numbers depend on the model and random seed.

### 4.1 Happy-path purchase

```text
"I want to buy 3 pairs of classic sunglasses and 1 pair of aviator sunglasses."
```

Expected behavior (TinyDB backend):

- The agent parses two items: "Classic" and "Aviator" with quantities
  3 and 1.
- It checks stock in `inventory_tbl`.
- For each item with sufficient stock:
  - Decreases `quantity_in_stock` accordingly.
  - Inserts one transaction per item, updating `balance_after_transaction`.
- Sets:
  - `ACTION="mutate"`, `SHOULD_MUTATE=True` (inside the generated code).
  - `STATUS="success"`.
  - `answer_text` summarizing the purchase.

### 4.2 Return (refund)

```text
"Return 2 Aviator sunglasses I bought last week."
```

Expected behavior:

- Treats this as a return.
- Increases Aviator stock by 2.
- Inserts a transaction with a negative amount (refund), updating the
  balance.
- `STATUS="success"`; `answer_text` confirms the refund.

### 4.3 Non-existent product

```text
"Do you have any unicorn sunglasses in stock under $50?"
```

Expected behavior:

- No matching inventory row for "unicorn".
- Depending on prompt mode, the code should:
  - Set `STATUS="no_match"`.
  - Suggest a closest alternative (e.g. by style or price) *if* any
    inventory exists, or politely indicate no suitable items.
  - Keep `ACTION="read"`, `SHOULD_MUTATE=False`.

### 4.4 Off-topic request

```text
"Can you reset my email password and unsubscribe me from all newsletters?"
```

Expected behavior:

- Outside the sunglasses inventory/transactions domain.
- The robust prompt asks the model to set:
  - `STATUS="unsupported_intent"`.
  - `answer_text` explaining that password resets/marketing
    preferences are not handled here, maybe suggesting contacting
    customer support.
- No mutations to inventory or transactions.

### 4.5 Invalid request (missing quantity)

```text
"I want to return Classic sunglasses."
```

Expected behavior:

- For a return, quantity is required but missing.
- The prompt instructs the model to set:
  - `STATUS="invalid_request"`.
  - `answer_text` asking succinctly for the missing information
    (e.g., "How many pairs would you like to return?").
- No state changes (read-only/dry-run semantics).

---

## 5. Looking Ahead: Domain-Specific Agentic Workflows

The patterns here are intended to be reusable:

- **Code-as-plan**: the LLM writes Python that becomes the
  executable plan.
- **Data abstraction**: stores (`CustomerServiceStore`) hide the
  backing DB (TinyDB, DuckDB, SQLite).
- **Prompt configuration**: `PromptConfig` as a structured way to
  manage prompt variants.

For future bio-specific or multiomics R&D workflows, you can:

- Swap the domain (e.g., inventory → experimental assays, transactions
  → experiment runs or budgets).
- Reuse the same patterns (single-agent, reflection, tool use,
  multi-agent orchestration) over more specialized tools and
  schemas.

This package aims to be a clean, testable unit you can evolve toward
those more advanced agentic systems.

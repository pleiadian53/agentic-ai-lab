# Customer Service Agent (Single-Agent, Code-as-Plan)

This package provides a reusable customer-service agent that you can
import from notebooks, scripts, or larger agentic workflows.

It implements a **single-agent** pattern where an LLM:

1. Reads a schema-aware prompt describing the inventory/transactions.
2. Generates Python code that *is* the plan ("code as action").
3. Executes that code in a controlled TinyDB environment.

The package is intentionally **decoupled** from the educational
`multiagent/M5_lab1` notebooks so it can be reused and extended
independently.

---

## Features

- **Two workflow modes:**
  - **Single-agent (code-as-plan):** LLM generates Python code that becomes the executable plan (flexible, powerful).
  - **Tool-based agent (plan-reflect-execute):** LLM generates structured plans using predefined tools (safe, observable).
- **DB abstraction:** Works with TinyDB, DuckDB, and SQLite backends via `CustomerServiceStore` interface.
- **Prompt configuration:** Switch between detailed and minimal prompts via `PromptConfig`.
- **Tool registry:** DB-agnostic tools for inventory queries, transactions, and validations.
- **Plan reflection:** LLM critiques and revises plans before execution.
- **Error explanation:** Human-readable error messages from failed executions.
- **Comprehensive tests:** Parametrized tests across all backend types.

---

## Package Layout

```text
multiagent/customer_service/
  __init__.py           # public API exports
  data_access.py        # CustomerServiceStore + TinyDB/DuckDB/SQLite stores
  tinydb_data.py        # TinyDB seed + schema helpers (standalone)
  relational_data.py    # pandas-based demo data (standalone)
  
  # Single-agent (code-as-plan)
  prompt_config.py      # PromptConfig + prompt builder
  planning.py           # generate_llm_code(...)
  execution.py          # extract_execute_block + execute_generated_code
  single_agent.py       # customer_service_agent(...) entrypoint
  cli_single.py         # CLI demo script
  
  # Tool-based agent (plan-reflect-execute)
  tool_registry.py      # TOOL_REGISTRY with DB-agnostic tools
  tool_planning.py      # generate_plan, reflect_on_plan, explain_execution_error
  tool_execution.py     # execute_plan with step-by-step validation
  tool_agent.py         # tool_based_agent(...) entrypoint
  cli_tool_agent.py     # CLI demo script
  
  tests/                # pytest test suite
  docs/                 # package-level documentation and examples
```

---

## Quickstart

### 1. Install dependencies

From the repo root, ensure your environment has the required
libraries (TinyDB, DuckDB, SQLite is in the stdlib, and the
OpenAI Python client):

```bash
pip install tinydb duckdb pandas openai python-dotenv
```

### 2. Set up your OpenAI API key

Create a `.env` file at the repo root (or configure environment
variables by another means):

```env
OPENAI_API_KEY=sk-...
```

The package uses `OpenAI()` from the `openai` library and will
pick up `OPENAI_API_KEY` from the environment.

### 3. Run the single-agent workflow with TinyDB

In a Python REPL, script, or notebook:

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
    reseed=True,   # start from fresh demo data
    client=client,
)

print("ANSWER:", result["exec"]["answer"])
print("STDOUT LOGS:\n", result["exec"]["stdout"])
```

The `result` dict includes:

- `question`: the original user request.
- `full_content`: raw LLM content (with `<execute_python>...</execute_python>`).
- `exec`:
  - `code`: extracted Python code body.
  - `stdout`: log lines printed by the generated code.
  - `error`: traceback text (or `None`).
  - `answer`: the final customer-facing `answer_text`.
  - `inventory_after`, `transactions_after`: TinyDB snapshots.

---

## Customizing the Planning Prompt

Prompt behavior is controlled via `PromptConfig` in
`prompt_config.py`.

```python
from multiagent.customer_service.prompt_config import PromptConfig
from multiagent.customer_service.planning import generate_llm_code

cfg = PromptConfig(mode="minimal")  # or "full"
content = generate_llm_code(
    prompt=question,
    inventory_tbl=inventory_tbl,
    transactions_tbl=transactions_tbl,
    model="o4-mini",
    temperature=0.5,
    prompt_config=cfg,
)
```

- `mode="full"` reproduces the detailed lab-style spec.
- `mode="minimal"` is shorter but keeps the key contracts:
  - Use TinyDB queries.
  - Set `answer_text` and `STATUS`.
  - Wrap code in `<execute_python>...</execute_python>`.

The `customer_service_agent(...)` helper uses `PromptConfig()`
implicitly (i.e., `mode="full"`) unless you later thread a config
into the underlying planning call.

See `docs/` for more structured prompt experiments.

---

## Using Different Backends

The single-agent executor is currently TinyDB-specific because it
executes code that expects `db`, `inventory_tbl`, and
`transactions_tbl` (TinyDB tables). However, the data layer is
pluggable:

- `TinyDBStore` (current default for `customer_service_agent`).
- `DuckDBStore` (pandas + DuckDB; for tools-only / multi-agent
  execution that uses SQL or DataFrames instead of TinyDB).
- `SQLiteStore` (file-backed SQL; similarly intended for future
  tools-only/multi-agent flows).

Example: initializing a DuckDB-backed store (for future workflows):

```python
from multiagent.customer_service import DuckDBStore

store = DuckDBStore()  # in-memory DuckDB
rows = store.get_inventory_rows()
```

The single-agent code-as-plan flow will continue to work with
`TinyDBStore`. New multi-agent or tools-only workflows can
rely on `DuckDBStore` / `SQLiteStore` directly.

---

## Tool Registry (Multi-Agent / Tool-Based Workflows)

The package now includes a **tool registry** (`tool_registry.py`) that mirrors the design from `M5_lab1/tools.py` but works with the `CustomerServiceStore` abstraction, supporting all backends (TinyDB, DuckDB, SQLite).

### Using the Tool Registry

```python
from multiagent.customer_service import (
    DuckDBStore,
    TOOL_REGISTRY,
    run_tools_for_step,
)

# Initialize store
store = DuckDBStore()

# Create context with store handle
context = {"__store__": store}

# Define a step with tools
step = {
    "tools": [
        {
            "use": "get_inventory_data",
            "result_key": "product",
            "args": {"product_name": "Aviator"}
        },
        {
            "use": "compute_total",
            "result_key": "total",
            "args": {"qty": 3, "price_from": "context.product.item.price"}
        }
    ]
}

# Execute the step
results = run_tools_for_step(step, context)

print(f"Product: {context['product']['item']['name']}")
print(f"Total: ${context['total']['amount']}")
```

### Available Tools

The registry includes:

- **READ tools:** `get_inventory_data`, `get_transaction_data`, `lookup_product`
- **WRITE tools:** `update_inventory`, `append_transaction`, `project_inventory`
- **PROPOSE tools:** `propose_transaction` (read-only simulation)
- **HELPER tools:** `compute_total`, `compute_refund`
- **VALIDATION tools:** `assert_true`, `assert_non_null`, `assert_gt`, `assert_nonnegative_stock`

All tools work with any `CustomerServiceStore` backend via the `store` parameter.

### Running Tests

```bash
# Run all tool registry tests across all backends
pytest multiagent/customer_service/tests/test_tool_registry.py -v

# Run tests for specific backend
pytest multiagent/customer_service/tests/test_tool_registry.py -v -k "duckdb"
```

---

## Tool-Based Agent (Plan-Reflect-Execute)

The package now includes a **tool-based agent** that implements the workflow from `M5_UGL_1.ipynb`:

### Using the Tool-Based Agent

```python
from openai import OpenAI
from multiagent.customer_service import tool_based_agent, DuckDBStore

client = OpenAI()
store = DuckDBStore()

result = tool_based_agent(
    "I want to return 2 Aviator sunglasses",
    store=store,
    client=client,
    use_reflection=True,  # LLM critiques and revises plan
    reseed=True
)

print(f"Success: {result['success']}")
print(f"Message: {result['message']}")

# Detailed report
from multiagent.customer_service import print_execution_report
print_execution_report(result)
```

### Workflow Steps

1. **Planning:** LLM generates structured plan with tool calls
2. **Reflection:** LLM critiques plan and fixes issues (optional)
3. **Execution:** Tools run step-by-step with validations
4. **Error Explanation:** Human-readable error messages (if needed)

### CLI Demo

```bash
# Run with custom prompt
run-customer-service-tool-agent --prompt "I want to buy 3 pairs of classic sunglasses" --verbose

# Run example suite
run-customer-service-tool-agent

# Skip reflection step
run-customer-service-tool-agent --no-reflection
```

### Comparison: Code-as-Plan vs Tool-Based

| Aspect | Code-as-Plan | Tool-Based |
|--------|--------------|------------|
| **Flexibility** | ✅ High - can express any logic | ❌ Limited to predefined tools |
| **Safety** | ❌ Executes arbitrary code | ✅ Constrained to safe operations |
| **Observability** | ❌ Opaque code execution | ✅ Explicit tool calls logged |
| **Debugging** | ❌ Harder to trace | ✅ Step-by-step validation |
| **LLM Usage** | ✅ Full reasoning power | ⚠️ More like template filling |
| **Best For** | Complex logic, exploration | Production, safety-critical |

**Recommendation:** Start with code-as-plan for flexibility, add tool-based layer when you need safety and observability.

---

## Where to Go Next

- See `docs/` for:
  - More detailed examples of prompt customization.
  - Side-by-side TinyDB vs DuckDB runs.
  - Example prompts (valid and invalid) and how the agent responds.
  - Tool registry usage patterns for multi-agent workflows.
- Run the CLI demos:

  ```bash
  # Code-as-plan (flexible)
  run-customer-service-single-agent --prompt "I want to buy 2 pairs of aviator sunglasses" --verbose
  
  # Tool-based (safe, observable)
  run-customer-service-tool-agent --prompt "I want to buy 2 pairs of aviator sunglasses" --verbose
  ```

- Future extensions you might build on this package:
  - Multi-agent customer service workflows (planner + reflector + executor) using the tool registry.
  - Bio-specific agentic workflows that reuse the same design patterns
    (reflection, tool use, code-as-plan, multi-agent) over
    domain-specific data.

# Tool-Based Agent Usage Guide

This guide explains how to use the tool-based customer service agent, which implements the plan-reflect-execute workflow from `M5_UGL_1.ipynb`.

## Overview

The tool-based agent provides an alternative to the code-as-plan approach:

- **Code-as-plan:** LLM generates Python code → Execute in sandbox
- **Tool-based:** LLM generates structured plan → Execute predefined tools

## Quick Start

```python
from openai import OpenAI
from multiagent.customer_service import tool_based_agent, DuckDBStore

client = OpenAI()
store = DuckDBStore()

result = tool_based_agent(
    "I want to buy 2 pairs of Aviator sunglasses",
    store=store,
    client=client,
    use_reflection=True,
    reseed=True
)

print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
```

## Workflow Steps

### 1. Planning

The LLM generates a structured plan specifying which tools to call:

```json
{
  "reasoning": "User wants to buy 2 Aviators. Lookup product, compute total, update inventory, record transaction.",
  "steps": [
    {
      "step_number": 1,
      "description": "Lookup product 'Aviator'",
      "tools": [
        {"use": "get_inventory_data", "args": {"product_name": "Aviator"}, "result_key": "prod"}
      ],
      "validations": [
        {"name": "product_found", "use_tool": "assert_true", "args": {"value_from": "context.prod.item"}}
      ]
    },
    {
      "step_number": 2,
      "description": "Compute purchase total",
      "tools": [
        {"use": "compute_total", "args": {"qty": 2, "price_from": "context.prod.item.price"}, "result_key": "total"}
      ],
      "validations": []
    }
    // ... more steps
  ]
}
```

### 2. Reflection (Optional)

The LLM critiques the draft plan and fixes issues:

- Wrong argument names (e.g., `quantity` → `qty`)
- Missing validations
- Incorrect tool usage

```python
result = tool_based_agent(
    prompt,
    use_reflection=True  # Enable reflection
)

# Access reflection output
print(result["reflection"]["critique"])
print(result["reflection"]["revised_plan"])
```

### 3. Execution

Tools run step-by-step with automatic state propagation:

```python
# Step 1: get_inventory_data runs
# → Result stored in context["prod"]

# Step 2: compute_total runs
# → Can reference context["prod"]["item"]["price"]

# Step 3: update_inventory runs
# → Store automatically updated

# Step 4: append_transaction runs
# → Transaction recorded
```

### 4. Error Explanation (If Needed)

If execution fails, get human-readable explanation:

```python
if not result["success"]:
    print(result["error_explanation"])
    # "Stock would go negative. Try reducing the quantity to 3 or less."
```

## API Reference

### `tool_based_agent()`

Main entry point for tool-based workflows.

```python
def tool_based_agent(
    user_query: str,
    store: Optional[CustomerServiceStore] = None,
    client: Optional[OpenAI] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1,
    use_reflection: bool = True,
    stop_on_failed_validation: bool = True,
    reseed: bool = False,
) -> dict[str, Any]:
```

**Parameters:**

- `user_query`: Natural language customer request
- `store`: CustomerServiceStore instance (defaults to DuckDBStore)
- `client`: OpenAI client (defaults to OpenAI())
- `model`: Model for planning/reflection (default: "gpt-4o-mini")
- `temperature`: Sampling temperature (default: 0.1)
- `use_reflection`: Enable reflection step (default: True)
- `stop_on_failed_validation`: Stop on first validation failure (default: True)
- `reseed`: Reseed store with fresh demo data (default: False)

**Returns:**

Dict with:
- `user_query`: Original request
- `draft_plan`: Initial plan from LLM
- `reflection`: Critique and revised_plan (if use_reflection=True)
- `final_plan`: Plan that was executed
- `execution_report`: Detailed step-by-step results
- `success`: Whether execution succeeded
- `message`: Human-readable summary
- `inventory_rows`: Final inventory state
- `transaction_rows`: Final transaction state
- `error_explanation`: Error explanation (if failed and use_reflection=True)

### `tool_based_agent_simple()`

Simplified interface returning just the message:

```python
message = tool_based_agent_simple(
    "I want to buy 3 pairs of classic sunglasses"
)
print(message)
# "Successfully executed 4 steps."
```

### `print_execution_report()`

Pretty-print detailed execution report:

```python
result = tool_based_agent(...)
print_execution_report(result)
```

## CLI Usage

### Basic Usage

```bash
# Run with custom prompt
run-customer-service-tool-agent --prompt "I want to buy 2 Aviator sunglasses"

# Run example suite
run-customer-service-tool-agent
```

### Options

```bash
# Skip reflection step
run-customer-service-tool-agent --no-reflection

# Verbose output (show detailed reports)
run-customer-service-tool-agent --verbose

# Use different model
run-customer-service-tool-agent --model gpt-4o

# Skip example suite after custom prompt
run-customer-service-tool-agent --prompt "..." --no-suite
```

## Advanced Usage

### Custom Store Backend

```python
from multiagent.customer_service import tool_based_agent, SQLiteStore

# Use SQLite instead of DuckDB
store = SQLiteStore(db_path="customer_service.db")

result = tool_based_agent(
    "I want to return 1 Sport sunglasses",
    store=store
)
```

### Disable Reflection for Speed

```python
# Skip reflection step (faster but less robust)
result = tool_based_agent(
    prompt,
    use_reflection=False
)
```

### Continue Execution on Validation Failure

```python
# Don't stop on first validation failure
result = tool_based_agent(
    prompt,
    stop_on_failed_validation=False
)
```

### Access Detailed Execution Report

```python
result = tool_based_agent(...)

for step in result["execution_report"]["steps"]:
    print(f"Step {step['step_number']}: {step['description']}")
    print(f"  Status: {step['step_ok']}")
    print(f"  Tools: {step['tools_run']}")
    
    for validation in step["validations"]:
        print(f"  Validation '{validation['name']}': {validation['ok']}")
```

## Example Scenarios

### Valid Purchase

```python
result = tool_based_agent(
    "I want to buy 2 pairs of Aviator sunglasses",
    reseed=True
)

assert result["success"]
assert len(result["execution_report"]["steps"]) == 4
# Steps: lookup → compute_total → update_inventory → append_transaction
```

### Valid Return

```python
result = tool_based_agent(
    "I'd like to return 1 pair of Sport sunglasses for a walk-in customer",
    reseed=True
)

assert result["success"]
# Steps: lookup → compute_refund → update_inventory (+1) → append_transaction
```

### Insufficient Stock

```python
result = tool_based_agent(
    "I want to buy 50 pairs of Mystique sunglasses",
    reseed=True
)

assert not result["success"]
assert "validation_failed" in result["execution_report"]["abort_reason"]
# Validation catches negative stock before mutation
```

### Product Not Found

```python
result = tool_based_agent(
    "I want to buy 2 pairs of Designer sunglasses",
    reseed=True
)

assert not result["success"]
# Validation catches missing product
```

## Comparison with Code-as-Plan

### When to Use Tool-Based

✅ **Use tool-based when:**
- You need **safety** (constrained actions)
- You need **observability** (explicit tool calls)
- You're building **production systems**
- You need **step-by-step validation**
- You want **structured error handling**

### When to Use Code-as-Plan

✅ **Use code-as-plan when:**
- You need **flexibility** (complex logic)
- You're **exploring** new workflows
- You need **adaptive reasoning**
- You want **fewer tool definitions**
- Performance is critical (fewer LLM calls)

### Hybrid Approach

Best of both worlds:

```python
# High-level: Tool-based for orchestration
plan = {
    "steps": [
        {"tool": "analyze_request", ...},
        {"tool": "execute_with_code", ...},  # ← Code-as-plan here
        {"tool": "validate_result", ...}
    ]
}
```

## Troubleshooting

### LLM Generates Invalid Plans

**Problem:** LLM uses wrong tool names or argument names

**Solution:** Enable reflection to catch and fix issues:

```python
result = tool_based_agent(
    prompt,
    use_reflection=True  # LLM will critique and fix plan
)
```

### Execution Fails with Validation Error

**Problem:** Validation catches issue (e.g., insufficient stock)

**Solution:** This is expected behavior! Check error explanation:

```python
if not result["success"]:
    print(result["error_explanation"])
    # Provides actionable guidance
```

### Tools Not Found

**Problem:** `ValueError: Unknown tool: xyz`

**Solution:** Check tool name against `TOOL_REGISTRY`:

```python
from multiagent.customer_service import TOOL_REGISTRY
print(list(TOOL_REGISTRY.keys()))
```

### Context References Not Resolving

**Problem:** `"price_from": "context.prod.item.price"` returns None

**Solution:** Ensure previous step stored result with correct `result_key`:

```json
{
  "step_number": 1,
  "tools": [
    {"use": "get_inventory_data", ..., "result_key": "prod"}  // ← Must match
  ]
}
```

## Next Steps

- See `TOOL_REGISTRY_USAGE.md` for tool registry details
- See `README.md` for package overview
- See `M5_UGL_1.ipynb` for original notebook implementation
- Try the CLI demo: `run-customer-service-tool-agent --verbose`

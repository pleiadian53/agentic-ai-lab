# Tool Registry Usage Guide

The `tool_registry` module provides a DB-agnostic tool API for LLM agents to interact with customer service data. It mirrors the design from `M5_lab1/tools.py` but works with any `CustomerServiceStore` backend (TinyDB, DuckDB, SQLite).

## Key Concepts

### 1. Tool Registry

The `TOOL_REGISTRY` is a dictionary mapping tool names to callable functions:

```python
from multiagent.customer_service import TOOL_REGISTRY

# Direct tool invocation
result = TOOL_REGISTRY["get_inventory_data"](
    store=store,
    product_name="Aviator"
)
```

### 2. Tool Signatures

`TOOL_SIGNATURES` defines required arguments for each tool:

```python
from multiagent.customer_service import TOOL_SIGNATURES

# Check what arguments a tool requires
required = TOOL_SIGNATURES["compute_total"]  # ["qty", "price"]
```

### 3. Context-Based Execution

Tools are typically executed within a context that provides the store and accumulates results:

```python
context = {
    "__store__": store,  # Required: CustomerServiceStore instance
    # Results from previous tools will be added here
}
```

## Basic Usage Examples

### Example 1: Product Lookup

```python
from multiagent.customer_service import DuckDBStore, TOOL_REGISTRY

# Initialize store
store = DuckDBStore()

# Look up a product
result = TOOL_REGISTRY["get_inventory_data"](
    store=store,
    product_name="Aviator"
)

print(f"Found {result['match_count']} items")
if result['item']:
    print(f"Product: {result['item']['name']}")
    print(f"Price: ${result['item']['price']}")
    print(f"Stock: {result['item']['quantity_in_stock']}")
```

### Example 2: Purchase Workflow

```python
from multiagent.customer_service import (
    TinyDBStore,
    TOOL_REGISTRY,
)

store = TinyDBStore()

# 1. Look up product
product = TOOL_REGISTRY["get_inventory_data"](
    store=store,
    product_name="Aviator"
)

if product['match_count'] == 1:
    item = product['item']
    
    # 2. Compute total
    total = TOOL_REGISTRY["compute_total"](
        qty=2,
        price=item['price']
    )
    
    # 3. Update inventory
    TOOL_REGISTRY["update_inventory"](
        store=store,
        item_id=item['item_id'],
        delta=-2
    )
    
    # 4. Record transaction
    txn = TOOL_REGISTRY["append_transaction"](
        store=store,
        customer_name="John Doe",
        summary=f"Purchase 2x {item['name']}",
        amount=total['amount']
    )
    
    print(f"Transaction {txn['transaction']['transaction_id']} completed")
    print(f"New balance: ${txn['transaction']['balance_after_transaction']}")
```

## Advanced Usage: Step-Based Execution

The `run_tools_for_step` function executes multiple tools in sequence, with automatic context resolution:

```python
from multiagent.customer_service import (
    SQLiteStore,
    run_tools_for_step,
)

store = SQLiteStore()
context = {"__store__": store}

# Define a multi-tool step
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
            "args": {
                "qty": 3,
                # Reference result from previous tool
                "price_from": "context.product.item.price"
            }
        },
        {
            "use": "update_inventory",
            "result_key": "inv_update",
            "args": {
                "item_id_from": "context.product.item.item_id",
                "delta": -3
            }
        },
        {
            "use": "append_transaction",
            "result_key": "txn",
            "args": {
                "customer_name": "Jane Smith",
                "summary": "Purchase 3x Aviator",
                "amount_from": "context.total.amount"
            }
        }
    ]
}

# Execute all tools in the step
results = run_tools_for_step(step, context)

# Results are available in context
print(f"Product: {context['product']['item']['name']}")
print(f"Total: ${context['total']['amount']}")
print(f"Transaction: {context['txn']['transaction']['transaction_id']}")
```

## Argument Canonicalization

The registry automatically normalizes argument names to handle LLM variations:

```python
from multiagent.customer_service import canonicalize_args

# LLM might use different names
args = {
    "quantity": 5,        # Will be mapped to "qty"
    "unit_price": 10.0,   # Will be mapped to "price"
}

canonical = canonicalize_args("compute_total", args)
# Result: {"qty": 5, "price": 10.0}
```

Supported mappings:

- **compute_total/compute_refund:**
  - `quantity` → `qty`
  - `unit_price` → `price`

- **get_inventory_data/lookup_product:**
  - `name`, `product`, `query` → `product_name`

- **update_inventory/project_inventory:**
  - `change` → `delta`
  - `new_quantity`, `quantity`, `qty_new` → `quantity_new`

- **propose_transaction/append_transaction:**
  - `transaction_summary` → `summary`

## Validation Tools

Use validation tools to check conditions before mutations:

```python
from multiagent.customer_service import run_tool_validation

store = DuckDBStore()
context = {"__store__": store}

# Define validation
validation = {
    "name": "check_sufficient_stock",
    "use_tool": "assert_nonnegative_stock",
    "args": {"item_id": "SG001"}
}

result = run_tool_validation(validation, context)

if result["ok"]:
    print(f"Stock check passed: {result['result']['qty']} units available")
else:
    print(f"Validation failed: {result.get('error', 'unknown')}")
```

## Working with Different Backends

All tools work identically across backends:

```python
from multiagent.customer_service import (
    TinyDBStore,
    DuckDBStore,
    SQLiteStore,
    TOOL_REGISTRY,
)

# Choose any backend
stores = [
    TinyDBStore(path=":memory:"),
    DuckDBStore(db_path=None),
    SQLiteStore(db_path=":memory:"),
]

for store in stores:
    result = TOOL_REGISTRY["get_inventory_data"](
        store=store,
        product_name="Aviator"
    )
    print(f"{store.__class__.__name__}: {result['match_count']} items")
```

## Error Handling

Tools return error dictionaries when operations fail:

```python
# Attempt to update non-existent item
result = TOOL_REGISTRY["update_inventory"](
    store=store,
    item_id="NONEXISTENT",
    quantity_new=10
)

if "error" in result:
    print(f"Error: {result['error']}")
    # Handle error appropriately
else:
    print(f"Updated: {result['updated']}")
```

## Integration with Multi-Agent Workflows

The tool registry is designed for multi-agent systems where:

1. **Planner agent** generates a plan with tool calls
2. **Executor agent** runs tools via `run_tools_for_step`
3. **Validator agent** checks results via `run_tool_validation`
4. **Reflector agent** analyzes outcomes and suggests corrections

Example plan structure:

```python
plan = {
    "steps": [
        {
            "description": "Look up product and compute total",
            "tools": [
                {"use": "get_inventory_data", "result_key": "product", "args": {...}},
                {"use": "compute_total", "result_key": "total", "args": {...}},
            ],
            "validations": [
                {"name": "check_stock", "use_tool": "assert_nonnegative_stock", "args": {...}},
            ]
        },
        {
            "description": "Execute purchase",
            "tools": [
                {"use": "update_inventory", "result_key": "inv_update", "args": {...}},
                {"use": "append_transaction", "result_key": "txn", "args": {...}},
            ]
        }
    ]
}

# Execute plan step by step
context = {"__store__": store}
for step in plan["steps"]:
    # Run validations first
    for validation in step.get("validations", []):
        result = run_tool_validation(validation, context)
        if not result["ok"]:
            raise ValueError(f"Validation failed: {result}")
    
    # Execute tools
    results = run_tools_for_step(step, context)
    print(f"Step completed: {step['description']}")
```

## Testing

The package includes comprehensive tests across all backends:

```bash
# Run all tool registry tests
pytest multiagent/customer_service/tests/test_tool_registry.py -v

# Run tests for specific backend
pytest multiagent/customer_service/tests/test_tool_registry.py -v -k "tinydb"
pytest multiagent/customer_service/tests/test_tool_registry.py -v -k "duckdb"
pytest multiagent/customer_service/tests/test_tool_registry.py -v -k "sqlite"

# Run specific test
pytest multiagent/customer_service/tests/test_tool_registry.py::test_complete_purchase_workflow -v
```

## Comparison with M5_lab1/tools.py

The customer_service tool registry maintains API compatibility with `M5_lab1/tools.py` but with key improvements:

| Feature | M5_lab1/tools.py | customer_service/tool_registry.py |
|---------|------------------|-----------------------------------|
| DB Backend | DuckDB only | TinyDB, DuckDB, SQLite via abstraction |
| Context Key | `__con__`, `__frames__` | `__store__` (unified interface) |
| Tool Signatures | Same | Same |
| Canonicalization | Same | Same |
| Step Execution | Same API | Same API, works with any backend |
| Testing | Manual | Parametrized pytest across all backends |

Migration from M5 lab code is straightforward:

```python
# M5 lab style
context = {
    "__con__": con,
    "__frames__": {"inventory_df": inv_df, "transaction_df": tx_df}
}

# Customer service style
context = {
    "__store__": DuckDBStore()  # Or TinyDBStore, SQLiteStore
}
```

## Next Steps

- See `README.md` for single-agent (code-as-plan) usage
- Explore `M5_lab1/M5_UGL_1.ipynb` for multi-agent workflow patterns
- Build custom tools by extending the registry
- Adapt patterns for domain-specific workflows (e.g., bio/multiomics data)

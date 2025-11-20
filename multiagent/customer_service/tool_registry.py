"""Tool registry for customer service agent with DB abstraction.

This module provides a tool-based API for LLM agents to interact with
customer service data (inventory, transactions) through a unified interface
that works with any CustomerServiceStore backend (TinyDB, DuckDB, SQLite, etc.).

The registry mirrors the design from M5_lab1/tools.py but operates on the
CustomerServiceStore abstraction rather than being tied to a specific DB.
"""

from __future__ import annotations

import re
from typing import Any, Callable, List, Optional

from .data_access import CustomerServiceStore


# =========================
# Type aliases
# =========================
ToolFn = Callable[..., dict[str, Any]]


# =========================
# READ tools
# =========================
def t_get_inventory_data(
    store: CustomerServiceStore,
    product_name: Optional[str] = None,
    item_id: Optional[str] = None
) -> dict[str, Any]:
    """Get inventory data by product name (case-insensitive) or item_id.
    
    Returns:
        {
            "rows": list[dict],      # All matching inventory rows
            "match_count": int,      # Number of matches
            "item": dict | None      # Single item dict if exactly one match
        }
    """
    all_rows = store.get_inventory_rows()
    
    if not product_name and not item_id:
        # No filters: return all
        rows = all_rows
    elif item_id:
        rows = [r for r in all_rows if r.get("item_id") == item_id]
    else:
        # Case-insensitive name match
        rows = [r for r in all_rows if r.get("name", "").lower() == product_name.lower()]
    
    item = rows[0] if len(rows) == 1 else None
    return {"rows": rows, "match_count": len(rows), "item": item}


def t_get_transaction_data(
    store: CustomerServiceStore,
    mode: str = "last_balance"
) -> dict[str, Any]:
    """Get transaction data.
    
    Args:
        store: CustomerServiceStore instance
        mode: "last_balance" returns last transaction ID and balance
        
    Returns:
        {"mode": str, "last_txn_id": str | None, "last_balance": float}
    """
    if mode == "last_balance":
        txns = store.get_transaction_rows()
        if not txns:
            return {"mode": mode, "last_txn_id": None, "last_balance": 0.0}
        last = txns[-1]
        return {
            "mode": mode,
            "last_txn_id": last.get("transaction_id"),
            "last_balance": float(last.get("balance_after_transaction", 0.0))
        }
    return {"mode": mode}


# =========================
# WRITE tools (mutate store state)
# =========================
def t_update_inventory(
    store: CustomerServiceStore,
    item_id: str,
    quantity_new: Optional[int] = None,
    delta: Optional[int] = None
) -> dict[str, Any]:
    """Update inventory quantity for an item.
    
    Args:
        store: CustomerServiceStore instance
        item_id: Item identifier
        quantity_new: Set to this absolute value (if provided)
        delta: Add this delta to current quantity (if provided)
        
    Returns:
        {"updated": {"item_id": str, "quantity_in_stock": int}} on success
        {"error": str} on failure
    """
    if item_id is None:
        return {"error": "item_id_missing"}
    
    rows = store.get_inventory_rows()
    item = next((r for r in rows if r.get("item_id") == item_id), None)
    if not item:
        return {"error": "item_not_found"}
    
    current = int(item.get("quantity_in_stock", 0))
    
    if delta is None and quantity_new is None:
        return {"error": "need_delta_or_quantity_new"}
    
    new_q = int(quantity_new) if quantity_new is not None else current + int(delta)
    store.update_inventory_quantity(item_id, new_q)
    
    return {"updated": {"item_id": item_id, "quantity_in_stock": new_q}}


def t_append_transaction(
    store: CustomerServiceStore,
    customer_name: str,
    summary: str,
    amount: float,
    txn_prefix: str = "TXN"
) -> dict[str, Any]:
    """Append a new transaction and update balance.
    
    Args:
        store: CustomerServiceStore instance
        customer_name: Customer name
        summary: Transaction description
        amount: Transaction amount (positive for sales, negative for refunds)
        txn_prefix: Prefix for transaction ID generation
        
    Returns:
        {"transaction": dict} with the new transaction record
    """
    last_bal = store.get_current_balance()
    new_bal = last_bal + float(amount)
    txn_id = store.next_transaction_id(txn_prefix)
    
    row = {
        "transaction_id": txn_id,
        "customer_name": customer_name,
        "transaction_summary": summary,
        "transaction_amount": float(amount),
        "balance_after_transaction": new_bal,
        "timestamp": ""  # Store implementations may add timestamp
    }
    
    store.insert_transaction(row)
    return {"transaction": row}


# =========================
# Propose-only (does not mutate, only computes)
# =========================
def t_propose_transaction(
    store: CustomerServiceStore,
    customer_name: str,
    summary: str,
    amount: float
) -> dict[str, Any]:
    """Propose a transaction without committing it.
    
    Returns what the transaction would look like with updated balance.
    """
    last_bal = store.get_current_balance()
    new_bal = last_bal + float(amount)
    
    return {
        "transaction_id": "AUTO_TXN",
        "customer_name": customer_name,
        "transaction_summary": summary,
        "transaction_amount": float(amount),
        "balance_after_transaction": new_bal
    }


# =========================
# Projection (alias for update with delta)
# =========================
def t_project_inventory(
    store: CustomerServiceStore,
    item_id: str,
    delta: int
) -> dict[str, Any]:
    """Project inventory change (alias for update_inventory with delta)."""
    return t_update_inventory(store=store, item_id=item_id, delta=delta)


# =========================
# Helper tools (calculations & validations)
# =========================
def t_compute_total(qty: int, price: float) -> dict[str, Any]:
    """Compute total amount for a purchase."""
    return {"amount": float(qty) * float(price)}


def t_compute_refund(qty: int, price: float) -> dict[str, Any]:
    """Compute refund amount (negative)."""
    return {"amount": -float(qty) * float(price)}


def t_assert_true(value: Any) -> dict[str, Any]:
    """Assert that a value is truthy."""
    return {"ok": bool(value)}


def t_assert_non_null(value: Any) -> dict[str, Any]:
    """Assert that a value is not None."""
    return {"ok": value is not None}


def t_assert_gt(value: float, threshold: float) -> dict[str, Any]:
    """Assert that value > threshold."""
    try:
        return {"ok": float(value) > float(threshold)}
    except Exception:
        return {"ok": False, "reason": "non_numeric"}


def t_assert_nonnegative_stock(store: CustomerServiceStore, item_id: str) -> dict[str, Any]:
    """Assert that an item has non-negative stock."""
    rows = store.get_inventory_rows()
    item = next((r for r in rows if r.get("item_id") == item_id), None)
    
    if not item:
        return {"ok": False, "reason": "item_not_found"}
    
    qty = int(item.get("quantity_in_stock", 0))
    return {"ok": qty >= 0, "qty": qty}


# =========================
# Tool registry
# =========================
TOOL_REGISTRY: dict[str, ToolFn] = {
    # READ
    "get_inventory_data": lambda **kw: t_get_inventory_data(
        kw["store"], kw.get("product_name"), kw.get("item_id")
    ),
    "get_transaction_data": lambda **kw: t_get_transaction_data(
        kw["store"], kw.get("mode", "last_balance")
    ),
    # Alias expected by some plans
    "lookup_product": lambda **kw: t_get_inventory_data(
        kw["store"], kw.get("product_name"), kw.get("item_id")
    ),
    
    # WRITE / mutate
    "update_inventory": lambda **kw: t_update_inventory(
        kw["store"], kw["item_id"], kw.get("quantity_new"), kw.get("delta")
    ),
    "append_transaction": lambda **kw: t_append_transaction(
        kw["store"], kw["customer_name"], kw["summary"], kw["amount"], kw.get("txn_prefix", "TXN")
    ),
    
    # Propose-only
    "propose_transaction": lambda **kw: t_propose_transaction(
        kw["store"], kw["customer_name"], kw["summary"], kw["amount"]
    ),
    
    # Projection alias
    "project_inventory": lambda **kw: t_project_inventory(
        kw["store"], kw["item_id"], kw["delta"]
    ),
    
    # Helpers
    "compute_total": lambda **kw: t_compute_total(kw["qty"], kw["price"]),
    "compute_refund": lambda **kw: t_compute_refund(kw["qty"], kw["price"]),
    
    # Validations
    "assert_true": lambda **kw: t_assert_true(kw["value"]),
    "assert": lambda **kw: t_assert_true(kw["value"]),  # alias
    "assert_non_null": lambda **kw: t_assert_non_null(kw["value"]),
    "assert_gt": lambda **kw: t_assert_gt(kw["value"], kw["threshold"]),
    "assert_nonnegative_stock": lambda **kw: t_assert_nonnegative_stock(kw["store"], kw["item_id"]),
}


# =========================
# Tool signatures (required args)
# =========================
TOOL_SIGNATURES: dict[str, List[str]] = {
    # READ
    "get_inventory_data": [],  # product_name or item_id optional
    "get_transaction_data": [],
    "lookup_product": [],
    
    # WRITE / mutate
    "update_inventory": ["item_id"],  # Also requires delta or quantity_new
    "append_transaction": ["customer_name", "summary", "amount"],
    "project_inventory": ["item_id", "delta"],
    
    # Propose-only
    "propose_transaction": ["customer_name", "summary", "amount"],
    
    # Helpers
    "compute_total": ["qty", "price"],
    "compute_refund": ["qty", "price"],
    
    # Validations
    "assert_true": ["value"],
    "assert": ["value"],
    "assert_non_null": ["value"],
    "assert_gt": ["value", "threshold"],
    "assert_nonnegative_stock": ["item_id"],
}


# =========================
# Argument canonicalization
# =========================
def canonicalize_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Normalize argument names to match tool signatures.
    
    This allows LLMs to use natural variations like 'quantity' vs 'qty',
    'unit_price' vs 'price', etc.
    """
    a = dict(args or {})
    
    # lookup_product / get_inventory_data
    if tool_name in ("lookup_product", "get_inventory_data"):
        if "product_name" not in a:
            for alt in ("name", "product", "query"):
                if alt in a and a[alt] is not None:
                    a["product_name"] = a.pop(alt)
                    break
    
    # compute_total / compute_refund: quantity->qty, unit_price->price
    if tool_name in ("compute_total", "compute_refund"):
        if "qty" not in a and "quantity" in a:
            a["qty"] = a.pop("quantity")
        if "price" not in a and "unit_price" in a:
            a["price"] = a.pop("unit_price")
    
    # update_inventory / project_inventory: change->delta, new_quantity->quantity_new
    if tool_name in ("update_inventory", "project_inventory"):
        if "delta" not in a and "change" in a:
            a["delta"] = a.pop("change")
        if "quantity_new" not in a:
            for alt in ("new_quantity", "quantity", "qty_new"):
                if alt in a and a[alt] is not None:
                    a["quantity_new"] = a.pop(alt)
                    break
    
    # propose/append_transaction: summary alias
    if tool_name in ("propose_transaction", "append_transaction"):
        if "summary" not in a and "transaction_summary" in a:
            a["summary"] = a.pop("transaction_summary")
    
    return a


def missing_required(tool_name: str, args: dict[str, Any]) -> List[str]:
    """Check for missing required arguments.
    
    Returns list of missing required argument names.
    """
    req = TOOL_SIGNATURES.get(tool_name, [])
    missing = [k for k in req if k not in args or args[k] is None]
    
    # Special rule: update_inventory needs delta or quantity_new
    if tool_name == "update_inventory" and ("delta" not in args and "quantity_new" not in args):
        missing.append("delta|quantity_new")
    
    return missing


# =========================
# Context resolution
# =========================
MISSING = object()


def get_from_context(ctx: dict[str, Any], path: str, default: Any = MISSING):
    """Resolve a dotted path from context (e.g., 'context.result.item.price')."""
    if not isinstance(path, str) or not path.startswith("context."):
        return path
    
    cur: Any = ctx
    for part in path.split(".")[1:]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def resolve_args(args: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Resolve arguments that reference context values.
    
    Args starting with 'context.' are resolved from the context dict.
    """
    out: dict[str, Any] = {}
    for k, v in (args or {}).items():
        if isinstance(v, str) and v.startswith("context."):
            val = get_from_context(ctx, v, default=None)
            out[k.replace("_from", "")] = val
        else:
            out[k] = v
    return out


# =========================
# Tool execution
# =========================
def run_tools_for_step(step: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Execute all tools in a step and update context.
    
    Args:
        step: Step dict with 'tools' list
        ctx: Context dict containing '__store__' (CustomerServiceStore)
        
    Returns:
        Dict mapping result_key -> tool result
        
    Raises:
        ValueError: If tool is unknown or required args are missing
    """
    results = {}
    
    for spec in step.get("tools", []):
        name = spec.get("use")
        rkey = spec.get("result_key")
        
        if not name or not rkey:
            raise ValueError("Each tool spec requires 'use' and 'result_key'")
        
        fn = TOOL_REGISTRY.get(name)
        if not fn:
            raise ValueError(f"Unknown tool: {name}")
        
        raw_args = spec.get("args", {})
        args = resolve_args(raw_args, ctx)
        args = canonicalize_args(name, args)
        
        missing = missing_required(name, args)
        if missing:
            raise ValueError(
                f"Missing required args for tool '{name}': {missing}. "
                f"Provided: {list(args.keys())}"
            )
        
        # Inject store handle
        args.setdefault("store", ctx["__store__"])
        
        res = fn(**args)
        
        # Store result in context
        ctx[rkey] = res
        results[rkey] = res
    
    return results


def run_tool_validation(v: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Run a validation tool and return result.
    
    Args:
        v: Validation spec with 'name', 'use_tool', 'args'
        ctx: Context dict containing '__store__'
        
    Returns:
        {"name": str, "ok": bool, "result": dict, "error": str (optional)}
    """
    name = v.get("name", "validation")
    tname = v.get("use_tool")
    
    fn = TOOL_REGISTRY.get(tname)
    if not fn:
        return {"name": name, "ok": False, "error": f"unknown_tool:{tname}"}
    
    raw_args = v.get("args", {})
    args = resolve_args(raw_args, ctx)
    args = canonicalize_args(tname, args)
    
    missing = missing_required(tname, args)
    if missing:
        return {
            "name": name,
            "ok": False,
            "error": f"missing_required_args:{tname}:{missing}",
            "provided_keys": list(args.keys()),
        }
    
    args.setdefault("store", ctx["__store__"])
    
    res = fn(**args)
    ok = bool(res.get("ok", True))
    return {"name": name, "ok": ok, "result": res}

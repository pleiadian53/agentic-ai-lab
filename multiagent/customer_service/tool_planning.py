"""LLM-based planning for tool-based customer service workflows.

This module provides functions for generating and refining plans that use
predefined tools from the tool_registry. It mirrors the planning approach
from M5_UGL_1.ipynb but works with the CustomerServiceStore abstraction.
"""

from __future__ import annotations

import json
import re
from typing import Any

from openai import OpenAI

from . import tool_registry


# =========================
# Planning specification
# =========================

PLANNING_SPEC_TOOLS_ONLY = """You are a senior data assistant. Plan customer service tasks using ONLY predefined tools.

AVAILABLE TOOLS:
1. get_inventory_data
   - args: { product_name?: string, item_id?: string }
   - returns: { rows: list, match_count: number, item: dict|null }

2. compute_total
   - args: { qty: number, price: number }
   - returns: { amount: number }

3. compute_refund
   - args: { qty: number, price: number }
   - returns: { amount: number } (negative)

4. update_inventory
   - args: { item_id: string, delta?: number, quantity_new?: number }
   - returns: { updated: { item_id: string, quantity_in_stock: number } }

5. append_transaction
   - args: { customer_name: string, summary: string, amount: number, txn_prefix?: string }
   - returns: { transaction: dict }

6. assert_true
   - args: { value: any }
   - returns: { ok: boolean }

7. assert_nonnegative_stock
   - args: { item_id: string }
   - returns: { ok: boolean, qty: number }

STRICT RULES:
1) Return VALID JSON ONLY with keys: reasoning, steps.
2) Each step MUST contain:
   - "step_number": integer
   - "description": short human text
   - "tools": an array of tool calls in order. Each tool call is:
       {"use": "<tool_name>", "args": {...}, "result_key": "<context_key>"}
     * You MAY reference previous results using dotted paths starting with "context.", e.g., "context.prod.item.price".
     * Use *_from to resolve from context, e.g., {"price_from": "context.prod.item.price"}.
     * Use ONLY the tools listed above.
     * Strings like the transaction summary MUST be composed inline by you (e.g., "Return 2 Sport sunglasses").
   - "validations": array of tool validations:
       {"name": "...", "use_tool": "<tool_name>", "args": {...}}
     * Allowed validation tools: assert_true, assert_nonnegative_stock ONLY.
     * Examples:
         - product_found: assert_true with {"value_from": "context.prod.item"} (non-null)
         - nonnegative_stock: assert_nonnegative_stock with {"item_id_from": "context.prod.item.item_id"}
3) For purchases/returns, include tool calls to:
   - Lookup product via get_inventory_data (case-insensitive by name)
   - (Purchase only) compute_total; (Return only) compute_refund
   - Create a clear summary STRING inline (e.g., "Purchase 3 Aviator sunglasses" / "Return 2 Sport sunglasses")
   - Update inventory via update_inventory (delta = -qty for purchases, +qty for returns)
   - Append the transaction via append_transaction (amount from compute_total/compute_refund)
4) Use canonical arg names exactly as in the Tool catalog:
   - quantity -> use qty
   - unit_price -> use price
   - Do NOT add extra args; compute_refund already returns negative amounts.

OUTPUT JSON SHAPE:
{
  "reasoning": "...",
  "steps": [
    {
      "step_number": 1,
      "description": "...",
      "tools": [ {"use": "...", "args": {...}, "result_key": "..."} ],
      "validations": [ {"name": "...", "use_tool": "...", "args": {...}} ]
    }
  ]
}

EXAMPLE (Return 2 Sport sunglasses for a walk-in):
{
  "reasoning": "User requests a return of 2 Sport units. We'll lookup product, compute a negative refund, update stock (+2), and append a refund transaction.",
  "steps": [
    {
      "step_number": 1,
      "description": "Lookup product 'Sport' and capture item details",
      "tools": [
        {"use": "get_inventory_data", "args": {"product_name": "Sport"}, "result_key": "prod"}
      ],
      "validations": [
        {"name": "product_found", "use_tool": "assert_true", "args": {"value_from": "context.prod.item"}}
      ]
    },
    {
      "step_number": 2,
      "description": "Compute refund amount for qty=2",
      "tools": [
        {"use": "compute_refund", "args": {"qty": 2, "price_from": "context.prod.item.price"}, "result_key": "refund"}
      ],
      "validations": []
    },
    {
      "step_number": 3,
      "description": "Update inventory by adding returned quantity",
      "tools": [
        {"use": "update_inventory", "args": {"item_id_from": "context.prod.item.item_id", "delta": 2}, "result_key": "inv_after"}
      ],
      "validations": [
        {"name": "stock_nonnegative", "use_tool": "assert_nonnegative_stock",
         "args": {"item_id_from": "context.prod.item.item_id"}}
      ]
    },
    {
      "step_number": 4,
      "description": "Append the refund transaction for a walk-in customer",
      "tools": [
        {"use": "append_transaction",
         "args": {
           "customer_name": "WALK_IN_CUSTOMER",
           "summary": "Return 2 Sport sunglasses",
           "amount_from": "context.refund.amount"
         },
         "result_key": "txn"}
      ],
      "validations": [
        {"name": "transaction_created", "use_tool": "assert_true",
         "args": {"value_from": "context.txn.transaction.transaction_id"}}
      ]
    }
  ]
}
"""


# =========================
# Planning functions
# =========================

def generate_plan(
    user_query: str,
    client: OpenAI,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1
) -> dict[str, Any]:
    """Generate a tool-based plan from a user query.
    
    Args:
        user_query: Natural language customer request
        client: OpenAI client instance
        model: Model to use for planning
        temperature: Sampling temperature
        
    Returns:
        Dict with "reasoning" and "steps" keys containing the plan
    """
    context = f"{PLANNING_SPEC_TOOLS_ONLY}\n\nCustomer query: {user_query}\nProduce the plan now."
    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Return JSON ONLY following the TOOLS-ONLY planning spec."},
            {"role": "user", "content": context},
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    
    return json.loads(resp.choices[0].message.content)


def reflect_on_plan(
    user_query: str,
    draft_plan: dict[str, Any],
    client: OpenAI,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1
) -> dict[str, Any]:
    """Reflect on and revise a draft plan.
    
    This function critiques the draft plan and produces a corrected version
    that follows the TOOLS-ONLY spec. It's useful for catching:
    - Wrong argument names (e.g., "quantity" instead of "qty")
    - Missing validations
    - Incorrect tool usage
    
    Args:
        user_query: Original customer request
        draft_plan: The draft plan to critique
        client: OpenAI client instance
        model: Model to use for reflection
        temperature: Sampling temperature
        
    Returns:
        Dict with "critique" (string) and "revised_plan" (dict) keys
    """
    sys = (
        "You are a senior plan reviewer. Return STRICT JSON with keys "
        "'critique' (string) and 'revised_plan' (object). The revised_plan MUST follow the TOOLS-ONLY spec."
    )
    
    user = (
        "TOOLS-ONLY PLANNING SPEC (enforce exactly):\n"
        f"{PLANNING_SPEC_TOOLS_ONLY}\n\n"
        "Customer query:\n"
        f"{user_query}\n\n"
        "Draft plan (JSON):\n"
        f"{json.dumps(draft_plan, ensure_ascii=False)}\n\n"
        "Task: Critique the draft against the spec and return a corrected 'revised_plan' if needed. "
        "Ensure valid JSON and that no raw SQL appears in the plan (only tool calls)."
    )
    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user}
        ],
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    
    data = _parse_json_or_repair(resp.choices[0].message.content)
    
    # Validate response structure
    if "revised_plan" not in data or not isinstance(data["revised_plan"], dict):
        if "steps" in data:
            # LLM returned plan directly without wrapper
            data = {"critique": "No explicit critique provided.", "revised_plan": data}
        else:
            # Malformed response, fall back to draft
            data = {
                "critique": "Malformed reflection output; falling back to draft.",
                "revised_plan": draft_plan
            }
    
    return data


def explain_execution_error(
    user_query: str,
    execution_report: dict[str, Any],
    client: OpenAI,
    model: str = "gpt-4o-mini",
    temperature: float = 0.1
) -> str:
    """Generate human-readable explanation of execution errors.
    
    Args:
        user_query: Original customer request
        execution_report: Execution report from execute_plan
        client: OpenAI client instance
        model: Model to use for explanation
        temperature: Sampling temperature
        
    Returns:
        Human-readable error explanation string
    """
    sys = (
        "You are a senior plan reviewer. Given a json with the report, "
        "explain in simple terms what went wrong and how to fix it."
    )
    
    user = (
        "Customer query:\n"
        f"{user_query}\n\n"
        "Execution report (JSON):\n"
        f"{json.dumps(execution_report, indent=2)}\n\n"
        "Task: Explain in simple terms what went wrong and how to fix it."
    )
    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys},
            {"role": "user", "content": user}
        ],
        temperature=temperature,
    )
    
    return resp.choices[0].message.content


# =========================
# Helper functions
# =========================

_ALLOWED_ESC = r'["\\/bfnrtu]'

def _repair_invalid_json_escapes(s: str) -> str:
    """Repair common JSON escape sequence errors."""
    s = s.replace("\\'", "'")
    return re.sub(rf'\\(?!{_ALLOWED_ESC})', r'', s)


def _parse_json_or_repair(s: str) -> dict[str, Any]:
    """Parse JSON with automatic repair of common escape issues."""
    try:
        return json.loads(s)
    except Exception:
        return json.loads(_repair_invalid_json_escapes(s))

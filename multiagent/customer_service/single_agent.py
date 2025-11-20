"""Single-agent customer service workflow (code-as-plan).

This module exposes a single entrypoint, ``customer_service_agent``,
that:

1. Uses an injected data store (currently TinyDB via TinyDBStore).
2. Generates a plan-as-code response from the LLM.
3. Executes the generated Python in a constrained environment.
4. Returns structured artifacts (raw content, executed code, stdout,
   answer, and final table snapshots).
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from openai import OpenAI

from .data_access import CustomerServiceStore, TinyDBStore
from .planning import generate_llm_code
from .execution import execute_generated_code


def customer_service_agent(
    question: str,
    *,
    store: Optional[CustomerServiceStore] = None,
    model: str = "o4-mini",
    temperature: float = 1.0,
    reseed: bool = False,
    client: Optional[OpenAI] = None,
) -> Dict[str, Any]:
    """Run the full single-agent workflow for a customer query.

    Args:
        question: Natural-language customer request.
        store: Optional data store implementation; if omitted, a
            TinyDBStore is created with default settings.
        model: OpenAI model name used for planning.
        temperature: Sampling temperature for the planner.
        reseed: If True, reseeds demo data before running the query.
        client: Optional OpenAI client instance.

    Returns:
        A dictionary with raw LLM content and execution artifacts, e.g.::

            {
              "question": "...",
              "full_content": "<execute_python>...",
              "exec": {
                  "code": "...",
                  "stdout": "...",
                  "error": None or "traceback...",
                  "answer": "short user-facing answer",
                  "inventory_after": [...],
                  "transactions_after": [...],
              },
            }
    """

    if store is None:
        store = TinyDBStore()

    if reseed:
        store.seed_demo_data()

    # Obtain low-level TinyDB handles for this run
    db, inventory_tbl, transactions_tbl = store.get_raw_handles()

    # 1) Generate plan-as-code (FULL content)
    full_content = generate_llm_code(
        question,
        inventory_tbl=inventory_tbl,
        transactions_tbl=transactions_tbl,
        model=model,
        temperature=temperature,
        client=client,
    )

    # 2) Execute the generated code
    exec_res = execute_generated_code(
        full_content,
        db=db,
        inventory_tbl=inventory_tbl,
        transactions_tbl=transactions_tbl,
        user_request=question,
    )

    # 3) Prepare return payload
    return {
        "question": question,
        "full_content": full_content,
        "exec": {
            "code": exec_res["code"],
            "stdout": exec_res["stdout"],
            "error": exec_res["error"],
            "answer": exec_res["answer"],
            "inventory_after": exec_res["inventory_tbl"],
            "transactions_after": exec_res["transactions_tbl"],
        },
    }

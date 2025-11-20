"""Prompt configuration and builder for the customer service agent.

This module provides a small abstraction around the large "code-as-plan"
prompt, so that variants (e.g., full vs. minimal, different tones,
stricter or looser policies) can be selected via a configuration object
instead of editing one giant string in-place.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


PromptMode = Literal["full", "minimal"]


@dataclass
class PromptConfig:
    """Configuration for the customer-service planning prompt.

    Attributes:
        mode: "full" keeps the detailed spec used in the lab notebook.
              "minimal" uses a shorter prompt that still encodes the key
              contracts but omits some prose and examples.
    """

    mode: PromptMode = "full"


# --- Prompt section templates ---

_FULL_PROMPT_TEMPLATE = """You are a senior data assistant. PLAN BY WRITING PYTHON CODE USING TINYDB.

Database Schema & Samples (read-only):
{schema_block}

Execution Environment (already imported/provided):
- Variables: db, inventory_tbl, transactions_tbl  # TinyDB Table objects
- Helpers: get_current_balance(tbl) -> float, next_transaction_id(tbl, prefix="TXN") -> str
- Natural language: user_request: str  # the original user message

PLANNING RULES (critical):
- Derive ALL filters/parameters from user_request (shape/keywords, price ranges "under/over/between", stock mentions,
  quantities, buy/return intent). Do NOT hard-code values.
- Build TinyDB queries dynamically with Query(). If a constraint isn't in user_request, don't apply it.
- Be conservative: if intent is ambiguous, do read-only (DRY RUN).

TRANSACTION POLICY (hard):
- Do NOT create aggregated multi-item transactions.
- If the request contains multiple items, create a separate transaction row PER ITEM.
- For each item:
  - compute its own line total (unit_price * qty),
  - insert ONE transaction with that amount,
  - update balance sequentially (balance += line_total),
  - update the item’s stock.
- If any requested item lacks sufficient stock, do NOT mutate anything; reply with STATUS="insufficient_stock".

HUMAN RESPONSE REQUIREMENT (hard):
- You MUST set a variable named `answer_text` (type str) with a short, customer-friendly sentence (1–2 lines).
- This sentence is the only user-facing message. No dataframes/JSON, no boilerplate disclaimers.
- If nothing matches, politely say so and offer a nearby alternative (closest style/price) or a next step.

ACTION POLICY:
- If the request clearly asks to change state (buy/purchase/return/restock/adjust):
    ACTION="mutate"; SHOULD_MUTATE=True; perform the change and write a matching transaction row.
  Otherwise:
    ACTION="read"; SHOULD_MUTATE=False; simulate and explain briefly as a dry run (in logs only).

FAILURE & EDGE-CASE HANDLING (must implement):
- Do not capture outer variables in Query.test. Pass them as explicit args.
- Always set a short `answer_text`. Also set a string `STATUS` to one of:
  "success", "no_match", "insufficient_stock", "invalid_request", "unsupported_intent".
- no_match: No items satisfy the filters → suggest the closest in style/price, or invite a different range.
- insufficient_stock: Item found but stock < requested qty → state available qty and offer the max you can fulfill.
- invalid_request: Unable to parse essential info (e.g., quantity for a purchase/return) → ask for the missing piece succinctly.
- unsupported_intent: The action is outside the store’s capabilities → provide the nearest supported alternative.
- In all cases, keep the tone helpful and concise (1–2 sentences). Put technical details (e.g., ACTION/DRY RUN) only in stdout logs.

OUTPUT CONTRACT:
- Return ONLY executable Python between these tags (no extra text):
  <execute_python>
  # your python
  </execute_python>

CODE CHECKLIST (follow in code):
1) Parse intent & constraints from user_request (regex ok).
2) Build TinyDB condition incrementally; query inventory_tbl.
3) If mutate: validate stock, update inventory, insert a transaction (new id, amount, balance, timestamp).
4) ALWAYS set:
   - `answer_text` (human sentence, required),
   - `STATUS` (see list above).
   Also print a brief log to stdout, e.g., "LOG: ACTION=read DRY_RUN=True STATUS=no_match".
5) Optional: set `answer_rows` or `answer_json` if useful, but `answer_text` is mandatory.

TONE EXAMPLES (for `answer_text`):
- success: "Yes, we have our Classic sunglasses, a round frame, for $60."
- no_match: "We don’t have round frames under $100 in stock right now, but our Moon round frame is available at $120."
- insufficient_stock: "We only have 1 pair of Classic left; I can reserve that for you."
- invalid_request: "I can help with that—how many pairs would you like to purchase?"
- unsupported_intent: "We can’t refurbish frames, but I can suggest similar new models."

Constraints:
- Use TinyDB Query for filtering. Standard library imports only if needed.
- Keep code clear and commented with numbered steps.

User request:
{question}
"""


_MINIMAL_PROMPT_TEMPLATE = """You are a data assistant for a sunglasses store.

You are given TinyDB tables `inventory_tbl` and `transactions_tbl`, and
helpers `get_current_balance(tbl)` and `next_transaction_id(tbl, prefix)`.
The variable `user_request` contains the user's natural-language query.

Write Python code that:
- Parses intent and parameters (item names, quantities, price ranges).
- Uses TinyDB Query objects to read from `inventory_tbl`.
- Decides whether the request is read-only (ACTION="read") or mutating
  (ACTION="mutate" with SHOULD_MUTATE=True).
- For mutating requests (purchases/returns), updates inventory and
  inserts one transaction per item with correct balances.
- Handles edge cases (no match, insufficient stock, invalid or
  unsupported requests) and sets a STATUS string accordingly.

Requirements:
- Always set `answer_text` to a short, customer-friendly sentence.
- Always set `STATUS` to one of: "success", "no_match",
  "insufficient_stock", "invalid_request", "unsupported_intent".
- Return ONLY executable Python inside:
  <execute_python>
  ...
  </execute_python>

User request:
{question}
"""


def build_customer_service_prompt(schema_block: str, question: str, config: PromptConfig | None = None) -> str:
    """Build the full user prompt for the planning call.

    If ``config`` is omitted, the original, detailed prompt is used. This
    preserves the lab notebook behavior while allowing future variants
    to be selected explicitly.
    """

    cfg = config or PromptConfig()

    if cfg.mode == "minimal":
        template = _MINIMAL_PROMPT_TEMPLATE
    else:
        template = _FULL_PROMPT_TEMPLATE

    return template.format(schema_block=schema_block, question=question)

"""CLI demo for the single-agent customer service workflow.

Usage examples (from repo root):

    python -m multiagent.customer_service.cli_single \
        --prompt "I want to buy 3 pairs of classic sunglasses and 1 pair of aviator sunglasses."

If no --prompt is provided, a small suite of example prompts (both
"happy path" and invalid/off-topic ones) will be executed against the
TinyDB demo backend.
"""

from __future__ import annotations

import argparse
import os
from typing import Iterable

from dotenv import load_dotenv
from openai import OpenAI

from . import TinyDBStore, customer_service_agent


EXAMPLE_PROMPTS: list[str] = [
    # Happy-path purchase
    "I want to buy 3 pairs of classic sunglasses and 1 pair of aviator sunglasses.",
    # Return / refund
    "Return 2 Aviator sunglasses I bought last week.",
    # Non-existent product
    "Do you have any unicorn sunglasses in stock under $50?",
    # Off-topic / unsupported
    "Can you reset my email password and unsubscribe me from all newsletters?",
    # Invalid (missing quantity for a return)
    "I want to return Classic sunglasses.",
]
def _summarize_items(rows, names=("Classic", "Aviator")) -> str:
    """Return a small textual summary for selected item names."""

    name_set = {n.lower() for n in names}
    selected = [r for r in rows if str(r.get("name", "")).lower() in name_set]
    if not selected:
        return "(no matching items)"
    lines: list[str] = []
    for r in selected:
        lines.append(
            f"- {r.get('name')} (item_id={r.get('item_id')}): qty={r.get('quantity_in_stock')}, price={r.get('price')}"
        )
    return "\n".join(lines)


def run_single_prompt(client: OpenAI, prompt: str, *, reseed: bool = False, verbose: bool = False) -> None:
    """Run one prompt through the customer_service_agent and print results."""

    store = TinyDBStore("store_db.json")

    inv_before = store.get_inventory_rows() if verbose else None
    bal_before = store.get_current_balance() if verbose else None

    result = customer_service_agent(
        prompt,
        store=store,
        model="o4-mini",
        temperature=1.0,
        reseed=reseed,
        client=client,
    )

    exec_res = result["exec"]

    print("\n=== USER PROMPT ===")
    print(prompt)

    if verbose:
        print("\n=== BEFORE: INVENTORY (Classic & Aviator) ===")
        print(_summarize_items(inv_before or []))
        print("\n=== BEFORE: BALANCE ===")
        print(f"{bal_before}")

    print("\n=== ANSWER_TEXT ===")
    print(exec_res["answer"])
    print("\n=== PLAN LOGS (stdout) ===")
    print(exec_res["stdout"] or "(no logs)")
    if exec_res["error"]:
        print("\n=== ERROR (traceback) ===")
        print(exec_res["error"])

    if verbose:
        inv_after = store.get_inventory_rows()
        bal_after = store.get_current_balance()
        print("\n=== AFTER: INVENTORY (Classic & Aviator) ===")
        print(_summarize_items(inv_after))
        print("\n=== AFTER: BALANCE ===")
        print(f"{bal_after}")


def run_suite(client: OpenAI, prompts: Iterable[str], *, verbose: bool = False) -> None:
    """Run a suite of prompts, reseeding before the first one."""

    for i, prompt in enumerate(prompts):
        reseed = i == 0
        run_single_prompt(client, prompt, reseed=reseed, verbose=verbose)
        print("\n" + "-" * 80 + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Single-agent customer service CLI demo")
    parser.add_argument(
        "--prompt",
        type=str,
        help="Single prompt to run. If omitted, a predefined suite of prompts is used.",
    )
    parser.add_argument(
        "--no-suite",
        action="store_true",
        help="If set with --prompt, do not run the default example suite.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print before/after inventory and balance for each prompt.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Configure it in your environment or .env file.")

    client = OpenAI()
    args = parse_args()

    if args.prompt:
        # Run the user-provided prompt first
        run_single_prompt(client, args.prompt, reseed=True, verbose=args.verbose)
        if not args.no_suite:
            # Then run the default examples without reseeding (continuing state)
            run_suite(client, EXAMPLE_PROMPTS, verbose=args.verbose)
    else:
        # No prompt given: run the default suite from a clean state
        run_suite(client, EXAMPLE_PROMPTS, verbose=args.verbose)


if __name__ == "__main__":  # pragma: no cover
    main()

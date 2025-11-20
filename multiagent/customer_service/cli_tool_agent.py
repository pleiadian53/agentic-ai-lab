"""CLI demo for tool-based customer service agent.

This script demonstrates the tool-based workflow (plan-reflect-execute)
as an alternative to the code-as-plan approach in cli_single.py.
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

from multiagent.customer_service import (
    DuckDBStore,
    tool_based_agent,
    print_execution_report,
)


# Example prompts demonstrating various scenarios
EXAMPLE_PROMPTS = [
    # Valid purchase
    "I want to buy 2 pairs of Aviator sunglasses",
    
    # Valid return
    "I'd like to return 1 pair of Sport sunglasses for a walk-in customer",
    
    # Invalid - insufficient stock
    "I want to buy 50 pairs of Mystique sunglasses",
    
    # Invalid - product not found
    "I want to buy 2 pairs of Designer sunglasses",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tool-based customer service agent demo"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Customer service prompt to process"
    )
    parser.add_argument(
        "--no-reflection",
        action="store_true",
        help="Skip reflection step (use draft plan directly)"
    )
    parser.add_argument(
        "--no-suite",
        action="store_true",
        help="Skip running example prompt suite"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed execution reports"
    )
    return parser.parse_args()


def run_single_prompt(client: OpenAI, prompt: str, args, reseed: bool = False):
    """Run a single prompt through the tool-based agent."""
    print("\n" + "=" * 70)
    print(f"PROMPT: {prompt}")
    print("=" * 70)
    
    store = DuckDBStore(db_path=None)  # In-memory
    if reseed:
        store.seed_demo_data()
    
    # Show initial state if verbose
    if args.verbose:
        print("\n--- Initial Inventory (Aviator & Sport) ---")
        inv_rows = store.get_inventory_rows()
        for row in inv_rows:
            if row["name"] in ["Aviator", "Sport"]:
                print(f"  {row['name']}: {row['quantity_in_stock']} in stock @ ${row['price']}")
        
        print(f"\n--- Initial Balance ---")
        print(f"  ${store.get_current_balance():.2f}")
    
    # Execute
    result = tool_based_agent(
        prompt,
        store=store,
        client=client,
        model=args.model,
        use_reflection=not args.no_reflection,
        reseed=False  # Already seeded above
    )
    
    # Print results
    if args.verbose:
        print()
        print_execution_report(result)
    else:
        print(f"\n{'✓' if result['success'] else '✗'} {result['message']}")
        
        if not result['success'] and 'error_explanation' in result:
            print(f"\nExplanation: {result['error_explanation']}")
    
    # Show final state if verbose
    if args.verbose:
        print("\n--- Final Inventory (Aviator & Sport) ---")
        inv_rows = result["inventory_rows"]
        for row in inv_rows:
            if row["name"] in ["Aviator", "Sport"]:
                print(f"  {row['name']}: {row['quantity_in_stock']} in stock @ ${row['price']}")
        
        print(f"\n--- Final Balance ---")
        print(f"  ${store.get_current_balance():.2f}")


def run_suite(client: OpenAI, prompts: list[str], args):
    """Run a suite of example prompts."""
    print("\n" + "=" * 70)
    print("RUNNING EXAMPLE PROMPT SUITE")
    print("=" * 70)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n[Example {i}/{len(prompts)}]")
        run_single_prompt(client, prompt, args, reseed=(i == 1))
        print()


def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set.", file=sys.stderr)
        print("Configure it in your environment or .env file.", file=sys.stderr)
        sys.exit(1)
    
    client = OpenAI()
    args = parse_args()
    
    print("=" * 70)
    print("TOOL-BASED CUSTOMER SERVICE AGENT")
    print("=" * 70)
    print(f"Model: {args.model}")
    print(f"Reflection: {'Enabled' if not args.no_reflection else 'Disabled'}")
    print(f"Verbose: {'Yes' if args.verbose else 'No'}")
    
    if args.prompt:
        # Run user-provided prompt
        run_single_prompt(client, args.prompt, args, reseed=True)
        
        if not args.no_suite:
            # Then run example suite
            run_suite(client, EXAMPLE_PROMPTS, args)
    else:
        # No prompt given: run example suite only
        run_suite(client, EXAMPLE_PROMPTS, args)
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Augmented Prompt Demo — Context-Enhanced LLM Queries

Demonstrates how injecting external data (housing listings) into an LLM prompt
produces grounded, factual answers vs. generic responses without context.

This is the "naive RAG" pattern: retrieve data → format → stuff into prompt → generate.
Later modules will replace manual formatting with vector-store retrieval.

Corresponds to: notebooks/RAG/C1M1/Lab2_LLM_calls_augmented_prompts.ipynb

Usage:
    mamba run -n agentic-ai python rag/examples/augmented_prompts/augmented_prompt_demo.py
"""

import json

from openai import OpenAI
from agentic_core.paths import load_project_env

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_project_env()

MODEL = "gpt-4o-mini"
MAX_TOKENS = 500

client = OpenAI()  # uses OPENAI_API_KEY from environment

# ---------------------------------------------------------------------------
# Sample data — small housing dataset
# ---------------------------------------------------------------------------
HOUSE_DATA = [
    {
        "address": "123 Maple Street",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "price": 230000,
        "year_built": 1998,
    },
    {
        "address": "456 Elm Avenue",
        "city": "Shelbyville",
        "state": "TN",
        "zip": "37160",
        "bedrooms": 4,
        "bathrooms": 3,
        "square_feet": 2500,
        "price": 320000,
        "year_built": 2005,
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, role: str = "user") -> str:
    """Send a single prompt to the LLM and return the response text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": role, "content": prompt}],
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content


def build_augmented_prompt(query: str, context_data: list[dict]) -> str:
    """
    Build a prompt with external context injected.

    Uses json.dumps for clean, automatic serialisation — no need for
    hand-crafted f-string layouts per data schema.
    """
    context = json.dumps(context_data, indent=2)
    return (
        "Use the following data to answer the user's query.\n\n"
        f"Data:\n{context}\n\n"
        f"Query: {query}"
    )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    query = "What is the most expensive house? And the bigger one?"

    # --- Without context ---
    print("=" * 60)
    print("WITHOUT context (generic LLM knowledge)")
    print("=" * 60)
    answer_no_context = ask(query)
    print(answer_no_context)

    # --- With augmented context ---
    print("\n" + "=" * 60)
    print("WITH augmented context (housing data injected)")
    print("=" * 60)
    augmented_prompt = build_augmented_prompt(query, HOUSE_DATA)
    answer_with_context = ask(augmented_prompt)
    print(answer_with_context)

    # --- Show the prompt that was sent ---
    print("\n" + "=" * 60)
    print("AUGMENTED PROMPT (what the LLM actually received)")
    print("=" * 60)
    print(augmented_prompt)


if __name__ == "__main__":
    main()

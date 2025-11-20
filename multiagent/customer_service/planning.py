"""Planning logic for the single-agent customer service workflow.

This module wraps the prompt and LLM call that generate "code-as-plan"
responses, as demonstrated in the M5_UGL_1_R notebook.
"""

from __future__ import annotations

from typing import Optional

from openai import OpenAI

from . import tinydb_data
from .prompt_config import PromptConfig, build_customer_service_prompt


def generate_llm_code(
    prompt: str,
    *,
    inventory_tbl,
    transactions_tbl,
    model: str = "o4-mini",
    temperature: float = 0.2,
    client: Optional[OpenAI] = None,
    prompt_config: Optional[PromptConfig] = None,
) -> str:
    """Generate a plan-with-code response from the LLM.

    This is a direct extraction of the notebook logic, with a couple of
    small tweaks for reuse:

    - The OpenAI client can be injected (for tests or alternative configs).
    - No notebook-specific rendering is performed here.
    """

    if client is None:
        client = OpenAI()

    schema_block = tinydb_data.build_schema_block(inventory_tbl, transactions_tbl)
    full_prompt = build_customer_service_prompt(
        schema_block=schema_block,
        question=prompt,
        config=prompt_config,
    )

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": "You write safe, well-commented TinyDB code to handle data questions and updates.",
            },
            {"role": "user", "content": full_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    return content

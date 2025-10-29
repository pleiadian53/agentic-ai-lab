"""LLM interaction functions for the research agent workflow."""

from __future__ import annotations

import aisuite as ai
from typing import Tuple

from .prompts import build_draft_prompt, build_reflection_prompt, build_revision_prompt


def generate_draft(
    *,
    topic: str,
    model: str,
    temperature: float,
    client: ai.Client,
) -> str:
    """
    Generate an initial essay draft on the given topic.
    
    Args:
        topic: The essay topic or question
        model: Model identifier (e.g., "openai:gpt-4o-mini")
        temperature: Sampling temperature
        client: aisuite client instance
        
    Returns:
        Generated essay draft text
    """
    prompt = build_draft_prompt(topic)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    
    return response.choices[0].message.content


def reflect_on_draft(
    *,
    draft: str,
    model: str,
    temperature: float,
    client: ai.Client,
) -> str:
    """
    Generate critical feedback on an essay draft.
    
    Args:
        draft: The essay text to critique
        model: Model identifier (e.g., "openai:gpt-4o")
        temperature: Sampling temperature
        client: aisuite client instance
        
    Returns:
        Structured feedback and critique
    """
    prompt = build_reflection_prompt(draft)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    
    return response.choices[0].message.content


def revise_draft(
    *,
    original_draft: str,
    reflection: str,
    model: str,
    temperature: float,
    client: ai.Client,
) -> str:
    """
    Revise an essay based on reflection feedback.
    
    Args:
        original_draft: The original essay text
        reflection: Critique and feedback
        model: Model identifier (e.g., "openai:gpt-4o")
        temperature: Sampling temperature
        client: aisuite client instance
        
    Returns:
        Revised essay text
    """
    prompt = build_revision_prompt(original_draft, reflection)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    
    return response.choices[0].message.content
